"""MeshData: a lightweight "schema.org for micron".

Page authors declare a page's type + metadata (and optional per-section types) in
an invisible '#'-comment head block; crawlers read it to categorize, snippet, and
rank. Names mirror schema.org/Dublin Core/OpenGraph. See SPEC.md.
"""
from .vocab import (VERSION, FIELDS, TYPES, ROBOTS, DEFAULT_ROBOTS,   # noqa: F401
                    is_type, schema_org, robots_policy)
from .parse import parse, has_meshdata                            # noqa: F401
from .emit import emit                                            # noqa: F401
from .infer import infer                                          # noqa: F401


def crawl_policy(md):
    """The crawl policy a parsed MeshData dict declares:
    {"index": bool, "follow": bool}.

    SCOPE: on a node's `/page/index.mu` this is the policy for the WHOLE node,
    because that page is the node speaking for itself. On any other page it
    applies to that page alone. A crawler that honours only one of the two
    should honour the node-level reading.
    """
    return robots_policy((md or {}).get("robots"))


def may_crawl(raw, path=None):
    """Convenience for crawlers holding raw micron rather than a parsed dict:
    False when the page declares it does not want to be indexed."""
    return crawl_policy(parse(raw)).get("index", True)


def describe(raw, path=None):
    """The one call a crawler wants: return declared MeshData if present, else a
    best-effort inference from page shape. Always returns a dict with a 'type'."""
    md = parse(raw)
    if md:
        md.setdefault("type", "index")
        return md
    return infer(raw, path)


__all__ = ["VERSION", "FIELDS", "TYPES", "ROBOTS", "DEFAULT_ROBOTS",
           "is_type", "schema_org", "robots_policy", "crawl_policy",
           "may_crawl", "parse", "has_meshdata", "emit", "infer", "describe"]
