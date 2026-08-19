# MeshData

A lightweight **"schema.org for micron"**. NomadNet page authors declare a page's
**type** and **metadata** in an invisible `#`-comment head block; crawlers (like
[Beacon](https://github.com/wdunn001/beacon)) read it to categorize pages, show
good result snippets, and rank them. Names mirror schema.org / Dublin Core /
OpenGraph, so a clearnet bridge is a rename, not a remodel. Part of the MeshAPI
family. **Full spec: [`SPEC.md`](SPEC.md).**

```
# +type: article
# +title: Guk Homecoming Arc, Part Three
# +author: wdunn001
# +date: 2026-08-16
# +description: The player is the unknowing second corruption.
# +tags: eqemu, lore, guk
# +lang: en
```

Invisible on every NomadNet client (they discard `#` lines), no extra fetch, no
duplication of visible content, tolerant line-scan parsing (a typo drops one line,
never the block). When a page has no MeshData, consumers **infer** type + title
from the page's shape rather than failing. Adoption is rewarded, not required.

## At a glance

**Head-block line:** `# +<field>: <value>` (the `+` sentinel distinguishes it
from an ordinary micron comment). One field per line, scanned anywhere in the file.

**Core fields (all optional):**

| field | meaning |
|-------|---------|
| `type` | the page type (see below); defaults to inferred/`index` |
| `title` | page title (else the first heading) |
| `author` | author name |
| `date` / `published` / `updated` | dates (refine recency; never fabricate it) |
| `description` | the result-snippet text (the `<head>`-meta equivalent) |
| `tags` | comma/semicolon list, **searchable keywords** (include the words people type) |
| `lang` | ISO language code |
| `image` | representative image path (`/file/...`) |
| `canonical` | logical-document URL, for cross-node dedupe of mirrors |

**Types** (each maps to a schema.org type, see `vocab`):
`index`, `article`, `blog`, `news`, `wiki`, `profile`, `service`,
`file-index`, `forum`, `status`, `media`, `dataset`, `event`, `product`.

**Commerce (`type: product`):** `price`, `currency` (ISO-4217), `availability`
(`in_stock` | `made_to_order` | `out_of_stock` | `digital`), `sku`, `vendor`,
and `shop`, the seller's MeshAPI destination hash (the "buy" doorway). A crawler's
shop view links a search result straight to the item.

```
# +type: product
# +title: RNode Kit v2
# +price: 79.00
# +currency: USD
# +availability: in_stock
# +sku: EO-RNODE-2
# +vendor: Ends & Oddity
# +shop: <MeshAPI destination hash of the seller's shop service>
# +tags: radio, lora, rnode
```

**Section map** lets you type *regions* of a page by referencing micron's
auto-slugged headings, with no content duplication:

```
# +section news = latest-headlines
# +section product = the-widget
```

MeshData is **inert** (it lives in comments; it never changes rendering) and
**adversarial** to any consumer that ranks on it. See SPEC §7 for the trust rules
(cap the schema bonus, sanity-check dates, cross-check declared vs inferred type).

## Package
```python
import meshdata
md = meshdata.describe(page_text, path)   # declared MeshData, else inferred; always has a type
meshdata.parse(page_text)                 # declared only ({} if none)
meshdata.emit({"type":"article","title":"...","tags":["a","b"]})   # build a head block
meshdata.schema_org("article")            # -> "Article"  (clearnet bridge)
```
Dependency-free.

## License
MIT.
