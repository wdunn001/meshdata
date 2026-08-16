"""Emit a MeshData head block (the invisible '#' comment lines) from a dict, for
Python page generators. Any language can emit the format; this is one reference.
Producers in other languages (e.g. The Mild Take's Node renderer) format the same
'# +key: value' lines directly.
"""
_ORDER = ("type", "title", "author", "date", "published", "updated",
          "description", "tags", "lang", "image", "canonical")


def emit(meta, sections=None):
    """meta: dict of MeshData fields (tags may be a list). sections: list of
    {type, anchor}. Returns the '#'-comment block as a string (no trailing NL)."""
    lines = []
    for k in _ORDER:
        v = meta.get(k)
        if v is None or v == "":
            continue
        if k == "tags" and isinstance(v, (list, tuple)):
            v = ", ".join(str(t) for t in v)
        v = str(v).replace("\n", " ").strip()
        lines.append(f"# +{k}: {v}")
    for s in (sections or meta.get("sections") or []):
        lines.append(f"# +section {s['type']} = {s['anchor']}")
    return "\n".join(lines)
