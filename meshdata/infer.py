"""Structural fallback: when a page carries no MeshData block (most pages, most
authors, at least at first), infer a type + title from the page's shape -- in the
spirit of the IndieWeb Post Type Discovery algorithm. Never hard-fail to
'uncategorized'.
"""
import re

from . import vocab

_HEAD = re.compile(r"^\s*>+\s*(.+)$")
_FILE_LINK = re.compile(r"`\[[^`]*`[^:\]]*:/file/")


def _clean(s):
    s = re.sub(r"`\[([^`\]]*)`[^\]]*\]", r"\1", s)          # link -> label
    s = re.sub(r"`[FBfb][0-9a-fA-F]{3}", "", s)             # colors
    s = re.sub(r"`[a-zA-Z!_=*<>]", "", s)                   # control toggles
    return s.replace("`", "").strip()


def infer(raw, path=None):
    """Best-effort {type, title, meshdata, inferred:True} from page shape."""
    md = {"meshdata": vocab.VERSION, "inferred": True}
    for line in (raw or "").splitlines():
        m = _HEAD.match(line)
        if m:
            t = _clean(m.group(1))
            if t:
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
        if len(d) > 20:
            md["description"] = d[:280]
            break
    return md
