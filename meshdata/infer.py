"""Structural fallback: when a page carries no MeshData block (most pages, most
authors, at least at first), infer a type + title from the page's shape, in the
spirit of the IndieWeb Post Type Discovery algorithm. Never hard-fail to
'uncategorized'.
"""
import re

from . import vocab

_HEAD = re.compile(r"^\s*>+\s*(.+)$")
_FILE_LINK = re.compile(r"`\[[^`]*`[^:\]]*:/file/")
_ASCII_ALNUM = re.compile(r"[A-Za-z0-9]")


def _clean(s):
    s = re.sub(r"`\[([^`\]]*)`[^\]]*\]", r"\1", s)          # link -> label
    s = re.sub(r"`[FBfb][0-9a-fA-F]{3}", "", s)             # colors
    s = re.sub(r"`[a-zA-Z!_=*<>]", "", s)                   # control toggles
    return s.replace("`", "").strip()


def _texty(s):
    """True if a line carries real searchable text. Block-art mastheads
    (███ ████), box drawing, and fancy-unicode letters (𝗕𝗘𝗔𝗖𝗢𝗡) carry ZERO ASCII
    alphanumerics, so a crawler must not lift them as a title. No filter can find
    them. Require a few plain [A-Za-z0-9] characters. (A page that wants a fancy
    visible title declares the real one in MeshData; this is the no-MeshData path.)"""
    return len(_ASCII_ALNUM.findall(s)) >= 3


def _clean_text(raw):
    """Whole document through _clean, line by line, so classify() sees the text a
    reader would see, with micron control codes stripped."""
    return "\n".join(_clean(l) for l in (raw or "").splitlines())


# --- structural type detectors (work on plain text, so a consumer can also
# --- reclassify already-extracted page text without refetching) ------------

# chat-log line: "[[Mon,23:07] <AMajor> hello" and close variants
_CHAT_MSG = re.compile(r"\[+\s*[A-Za-z]{2,3},?\s?\d{1,2}:\d{2}\s*\]+\s*<[^<>\n]{1,32}>")
# generic timestamped <nick> message line
_NICK_LINE = re.compile(r"^\s*\[[^\]\n]{2,24}\]\s*<[^<>\s][^<>\n]{0,30}>\s+\S", re.M)
_FORUM_HINT = re.compile(r"forum|bbs|comboard|messageboard|guestbook|read_board")
_FORUM_TEXT = re.compile(r"\b(forum|board|topics?|threads?|discussions?|replies)\b")
_STATUS_MARKS = (re.compile(r"\buptime\b"), re.compile(r"transport instance"),
                 re.compile(r"shared instance"), re.compile(r"\btraffic\b"),
                 re.compile(r"connected peers|\bpeers\b"),
                 re.compile(r"\b(rns|reticulum) ?(version|status)\b"),
                 re.compile(r"\brate ?:"))
_WIKI_SECTIONS = (re.compile(r"\breferences\b"), re.compile(r"external links"),
                  re.compile(r"\bsee also\b"), re.compile(r"\bbibliography\b"),
                  re.compile(r"from wikipedia"))


def classify(text, path=None, title=None):
    """Structural page type from extracted TEXT (micron already stripped), or
    None when no specific shape matches. Order matters: the most distinctive
    shapes first, so a chat log on a forum node still reads as chat."""
    tl = (text or "").lower()
    pl = ((path or "") + " " + (title or "")).lower()
    if len(_CHAT_MSG.findall(text or "")) >= 3 or len(_NICK_LINE.findall(text or "")) >= 5:
        return "chat"
    if "chat" in pl and (_CHAT_MSG.search(text or "") or _NICK_LINE.search(text or "")):
        return "chat"
    if _FORUM_HINT.search(pl):
        return "forum"
    if "login" in tl and "register" in tl and _FORUM_TEXT.search(tl):
        return "forum"
    status_hits = sum(1 for m in _STATUS_MARKS if m.search(tl))
    if status_hits >= 2 or (re.search(r"\bstat(us|s)\b", pl) and status_hits >= 1):
        return "status"
    if re.search(r"(^|/)wiki(/|\b)", pl):
        return "wiki"
    if sum(1 for m in _WIKI_SECTIONS if m.search(tl)) >= 2:
        return "wiki"
    return None


def infer(raw, path=None):
    """Best-effort {type, title, meshdata, inferred:True} from page shape."""
    md = {"meshdata": vocab.VERSION, "inferred": True}
    for line in (raw or "").splitlines():
        m = _HEAD.match(line)
        if m:
            t = _clean(m.group(1))
            if t and _texty(t):            # skip art/decoration-only headings
                md["title"] = t[:200]
                break
    p = (path or "").lower().rstrip("/")
    shaped = classify(_clean_text(raw), path=p, title=md.get("title"))
    if shaped:
        md["type"] = shaped
    elif p in ("", "/page/index.mu") or p.endswith("/page/index.mu"):
        md["type"] = "index"
    elif len(_FILE_LINK.findall(raw or "")) >= 3:
        md["type"] = "file-index"
    else:
        md["type"] = "article"
    # a rough description = first non-empty body paragraph
    for line in (raw or "").splitlines():
        if line.lstrip().startswith(("#", ">", "-", "`=")) or not line.strip():
            continue
        d = _clean(line)
        if len(d) > 20 and _texty(d):
            md["description"] = d[:280]
            break
    return md
