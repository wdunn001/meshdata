"""MeshData 0.1 vocabulary: the small, fixed core field + type sets.

Deliberately DC/OpenGraph-sized (a handful of fields, ~dozen types), with names
mirroring schema.org / Dublin Core / OpenGraph so a future clearnet bridge is a
rename, not a remodel.
"""
VERSION = "0.1"

# Core page-level fields (all optional). Names map to schema.org/DC/OG.
FIELDS = ("type", "title", "author", "date", "published", "updated",
          "description", "tags", "lang", "image", "canonical")

# Page-type taxonomy. maps_to = the nearest schema.org type (for a future bridge).
TYPES = {
    "index":      "WebSite",            # a node's home / landing page
    "article":    "Article",
    "blog":       "BlogPosting",
    "news":       "NewsArticle",
    "wiki":       "Article",
    "profile":    "ProfilePage",        # a node/person profile
    "service":    "WebAPI",             # a MeshAPI service front
    "file-index": "DataCatalog",        # a directory of downloadable files
    "forum":      "DiscussionForumPosting",
    "status":     "WebPage",            # a dashboard/status page
    "media":      "MediaObject",        # image/audio/video index
    "dataset":    "Dataset",
    "event":      "Event",
}

DEFAULT_TYPE = "index"


def is_type(t):
    return t in TYPES


def schema_org(t):
    return TYPES.get(t)
