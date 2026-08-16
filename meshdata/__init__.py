"""MeshData: a lightweight "schema.org for micron".

Page authors declare a page's type + metadata (and optional per-section types) in
an invisible '#'-comment head block; crawlers read it to categorize, snippet, and
rank. Names mirror schema.org/Dublin Core/OpenGraph. See SPEC.md.
"""
from .vocab import VERSION, FIELDS, TYPES, is_type, schema_org   # noqa: F401
from .parse import parse, has_meshdata                            # noqa: F401
from .emit import emit                                            # noqa: F401
from .infer import infer                                          # noqa: F401


def describe(raw, path=None):
    """The one call a crawler wants: return declared MeshData if present, else a
    best-effort inference from page shape. Always returns a dict with a 'type'."""
    md = parse(raw)
    if md:
        md.setdefault("type", "index")
        return md
    return infer(raw, path)


__all__ = ["VERSION", "FIELDS", "TYPES", "is_type", "schema_org",
           "parse", "has_meshdata", "emit", "infer", "describe"]
