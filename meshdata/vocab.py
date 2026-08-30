"""MeshData 0.2 vocabulary: the small, fixed core field + type sets.

Deliberately DC/OpenGraph-sized (a handful of fields, ~dozen types), with names
mirroring schema.org / Dublin Core / OpenGraph so a future clearnet bridge is
just a rename.
"""
import re

VERSION = "0.2"

# Core page-level fields (all optional). Names map to schema.org/DC/OG.
FIELDS = ("type", "title", "author", "date", "published", "updated",
          "description", "tags", "lang", "image", "canonical", "robots")

# Commerce fields, meaningful when type == "product". Names mirror schema.org
# Product/Offer (price/priceCurrency/availability/sku/brand -> a clearnet
# bridge is a rename). `shop` = the MeshAPI destination hash where buy ops
# (catalog/cart/order) live. It is the doorway from a search result to a seller.
COMMERCE_FIELDS = ("price", "currency", "availability", "sku", "vendor", "shop")
AVAILABILITY = ("in_stock", "made_to_order", "out_of_stock", "digital")

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
    "chat":       "Conversation",       # a live chat room / chat log page
    "status":     "WebPage",            # a dashboard/status page
    "media":      "MediaObject",        # image/audio/video index
    "dataset":    "Dataset",
    "event":      "Event",
    "product":    "Product",           # a purchasable item (see COMMERCE_FIELDS)
}

# Crawl policy (0.2). Token names are robots.txt / X-Robots-Tag's, so they are
# already familiar to anyone who has published on the clearnet and a bridge
# stays a rename rather than a remodel. Comma- or space-separated.
#
#   all       index this page and follow its links (the default)
#   index     index this page
#   noindex   do NOT index this page
#   follow    follow the links found on this page
#   nofollow  do NOT follow the links found on this page
#   none      shorthand for "noindex, nofollow"
#
# A page saying nothing is NOT a refusal, it is simply no statement, and the
# default stands. MeshData describes pages their author already published.
ROBOTS = ("all", "index", "noindex", "follow", "nofollow", "none")
DEFAULT_ROBOTS = "all"


def robots_policy(value):
    """Resolve a `robots` field value into {"index": bool, "follow": bool}.

    Tolerant like every other MeshData read: unknown tokens are ignored instead
    of voiding the declaration. When tokens conflict the RESTRICTIVE one wins
    ("index, noindex" is noindex), because misreading a refusal as permission
    costs somebody else their bandwidth, while misreading permission as a
    refusal only costs the crawler some index.
    """
    index = follow = True
    for tok in re.split(r"[\s,;]+", (value or "").strip().lower()):
        if tok == "none":
            index = follow = False
        elif tok == "noindex":
            index = False
        elif tok == "nofollow":
            follow = False
        # "all"/"index"/"follow" affirm the default; unknown tokens are ignored
    return {"index": index, "follow": follow}


DEFAULT_TYPE = "index"


def is_type(t):
    return t in TYPES


def schema_org(t):
    return TYPES.get(t)
