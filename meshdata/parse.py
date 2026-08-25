"""Parse a MeshData head block out of a micron (.mu) page.

MeshData rides micron's invisible '#' comment lines, distinguished from ordinary
comments by a '+' sentinel (org-mode style), so it renders as nothing on every
NomadNet client and never duplicates the visible content:

    # +type: article
    # +title: Guk Homecoming Arc, Part Three
    # +author: wdunn001
    # +date: 2026-08-16
    # +description: The player is the unknowing second corruption.
    # +tags: eqemu, lore, guk
    # +lang: en
    # +section news = latest-headlines      (maps a micron heading slug to a type)

Parsing is a tolerant line scan (no JSON, so a single typo can't void the block).
"""
import re

from . import vocab

_FIELD = re.compile(r"^#\s*\+([a-zA-Z][\w-]*)\s*:\s*(.*)$")
_SECTION = re.compile(r"^#\s*\+section\s+([\w./-]+)\s*=\s*([^\s#]+)\s*$", re.I)


def parse(raw):
    """Return a MeshData dict from micron text, or {} if no MeshData markers.
    Keys: meshdata (version), type, title, author, date/published/updated,
    description, tags (list), lang, image, canonical, sections (list of
    {type, anchor})."""
    md = {}
    sections = []
    for line in (raw or "").splitlines():
        s = line.rstrip()
        if not s.lstrip().startswith("#"):
            continue
        msec = _SECTION.match(s)
        if msec:
            sections.append({"type": msec.group(1).lower(), "anchor": msec.group(2)})
            continue
        mf = _FIELD.match(s)
        if not mf:
            continue
        key, val = mf.group(1).lower(), mf.group(2).strip()
        if key == "section":  # "# +section: news = slug" alt form
            alt = re.match(r"([\w./-]+)\s*=\s*([^\s#]+)", val)
            if alt:
                sections.append({"type": alt.group(1).lower(), "anchor": alt.group(2)})
            continue
        if key in ("tags", "keywords"):
            md["tags"] = [t.strip() for t in re.split(r"[;,]", val) if t.strip()]
        # Commerce fields (price/currency/availability/sku/vendor/shop) ride
        # the same tolerant head block, gated by their own vocab set since
        # they're only meaningful for type=="product". They are parsed here
        # unconditionally like every other field. Declaring a field that
        # doesn't apply to your type is harmless and does not cause an error.
        elif key in vocab.FIELDS or key in vocab.COMMERCE_FIELDS or key == "meshdata":
            md[key] = val
    if sections:
        md["sections"] = sections
    if md:
        md.setdefault("meshdata", vocab.VERSION)
    return md


def has_meshdata(raw):
    return bool(parse(raw))
