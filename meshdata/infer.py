"""Structural fallback: when a page carries no MeshData block (most pages, most
authors, at least at first), infer a type + title from the page's shape -- in the
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
    """True if a line is real searchable text, not decoration. Block-art mastheads
    (███ ████), box drawing, and fancy-unicode letters (𝗕𝗘𝗔𝗖𝗢𝗡) carry ZERO ASCII
    alphanumerics, so a crawler must not lift them as a title -- no filter can find
    them. Require a few plain [A-Za-z0-9] characters. (A page that wants a fancy
    visible title declares the real one in MeshData; this is the no-MeshData path.)"""
    return len(_ASCII_ALNUM.findall(s)) >= 3


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
    if p in ("", "/page/index.mu") or p.endswith("/page/index.mu"):
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
