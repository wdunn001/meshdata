# MeshData 0.1 — structured data for micron pages

MeshData is a "schema.org for micron": a tiny way for a NomadNet page author to
declare a page's **type** and **metadata** so crawlers (like Beacon) can
categorize it, show good result snippets, and rank it. Names mirror schema.org /
Dublin Core / OpenGraph so a clearnet bridge is a rename, not a remodel.

## 1. The head block (invisible)

MeshData rides micron's `#` comment lines — which every NomadNet client discards
(never rendered) — distinguished from ordinary comments by a `+` sentinel. So
metadata adds no visible clutter, no separate fetch, and no risk to legacy pages:

```
# +type: article
# +title: Guk Homecoming Arc, Part Three
# +author: wdunn001
# +date: 2026-08-16
# +description: The player is the unknowing second corruption.
# +tags: eqemu, lore, guk
# +lang: en
```

Put it at the top of the `.mu` by convention; a parser MAY scan the whole file
(the lines are invisible wherever they sit). Parsing is a **tolerant line scan**,
never JSON — a single typo drops one line, never the whole block.

### Fields (all optional)
`type`, `title`, `author`, `date` (or `published` / `updated`), `description`,
`tags` (comma/semicolon list), `lang`, `image`, `canonical`. `description` is what
a search engine shows as the result snippet — the `<head>`-meta equivalent.

### Types (a dozen-plus, DC/OG-sized)

Each maps 1:1 to a schema.org type, so a clearnet bridge is a rename. The full
taxonomy (the reference `vocab`):

| MeshData type | schema.org | use |
|---------------|-----------|-----|
| `index`       | WebSite            | a node's home / landing page |
| `article`     | Article            | a general written page |
| `blog`        | BlogPosting        | a dated post |
| `news`        | NewsArticle        | a news item (timely, sourced) |
| `wiki`        | Article            | an encyclopedia article |
| `profile`     | ProfilePage        | a node/person profile |
| `service`     | WebAPI             | a MeshAPI service front |
| `file-index`  | DataCatalog        | a directory of downloadable files |
| `forum`       | DiscussionForumPosting | a thread / board |
| `status`      | WebPage            | a dashboard / status page |
| `media`       | MediaObject        | an image/audio/video index |
| `dataset`     | Dataset            | a structured data collection |
| `event`       | Event              | a scheduled happening |
| `product`     | Product/Offer      | a purchasable item — see §6 |

Unknown types are ignored, not errors (§4); a consumer falls back to inference.
Default when absent and unclear: `index`.

## 2. Section map (typing parts of a page)

To tag *regions* of a page (e.g. "these headings are news"), reference micron's
auto-slugged headings from the same hidden block — no duplication of the visible
content:

```
# +section news = latest-headlines
# +section service = api-explorer
```

`# +section <type> = <heading-anchor>` where `<heading-anchor>` is the slug micron
generates for a `>` heading. A crawler can then attribute the content under that
heading to the given type.

## 3. Consumption + graceful fallback

A crawler calls `describe(page, path)`: return the declared MeshData if present,
else **infer** from page shape (first heading → title; a table of `/file/` links →
`file-index`; `/page/index.mu` → `index`; else `article`). Never hard-fail to
"uncategorized" — most pages won't be annotated at first, and adoption is rewarded
with better categorization/ranking rather than required.

## 4. Rules

- MeshData is **inert**: it MUST NOT affect how the page renders (it can't — it's
  in comments). A consumer MUST NOT execute or trust it as input validation.
- Unknown fields/types are ignored, not errors.
- The format is language-agnostic; the `meshdata` Python package is one reference
  implementation (parse / emit / infer). Producers in any language format the same
  `# +key: value` lines.

## 5. Versioning
`0.1`. An optional `# +meshdata: 0.1` line may state the version; absence implies
current. Unknown versions: read what you understand.

## 6. Commerce extension (0.1): `type: product`

A purchasable item is a page (or section) typed `product`, with commerce fields
mirroring schema.org `Product`/`Offer`:

```
# +type: product
# +title: RNode Kit v2
# +description: Assembled 433MHz RNode, case, antenna.
# +price: 79.00
# +currency: USD
# +availability: in_stock
# +sku: EO-RNODE-2
# +vendor: Ends & Oddity
# +shop: <MeshAPI destination hash of the seller's shop service>
# +tags: radio, lora
```

- `price` is a decimal string; `currency` an ISO-4217 code.
- `availability`: `in_stock` | `made_to_order` | `out_of_stock` | `digital`.
- `shop` is the **doorway**: the MeshAPI destination whose ops (catalog/cart/
  order) actually sell the item — a crawler's shop view links search results
  straight to the seller's own node/service. Reference consumer: Beacon's
  `type: product` filter. Reference producer: rns-stall.
- Multiple products on one page: use the section map (`# +section product = <slug>`)
  with one page-level block per page remaining the primary record, or one page
  per product (preferred — cleaner crawl units).

## 7. News extension (0.1): `type: news`

A news item is a page typed `news` (a `NewsArticle`), with a few fields on top of
the core set:

```
# +type: news
# +title: Heat-related illnesses spike in Colorado
# +author: Colorado Sun          # the outlet
# +publisher: Colorado Sun       # the outlet (schema.org Organization)
# +date: 2026-08-17 14Z
# +description: A record heat wave is straining rural clinics.
# +region: Denver                # the locality the story is about
# +category: health              # the topic / desk
# +tags: colorado, denver, health, news
# +canonical: https://coloradosun.com/2026/08/17/...   # source URL
# +lang: en
```

- `region` — the place the story concerns (a city or state). A consumer can offer
  localized results (Beacon matches it to a reader's saved area). Fold the same
  value into `tags` too, so it is searchable even by consumers that ignore `region`.
- `category` — the topic/desk. **This is a plain field, NOT the reserved
  `# +section` directive (§2)** — `section` always means the region-typing map.
- `publisher` — the outlet, mirroring schema.org `Organization` (usually equal to
  `author` for syndicated news).
- `canonical` — the original source URL: dedupes a story mirrored across many mesh
  nodes, and lets a consumer trust the source's own timestamp.

Reference producer: rns-news. Reference consumer: Beacon's `type: news` filter and
its localized "just my area" news.

## 8. Consumer guidance (ranking & trust)

MeshData is author-declared and therefore an adversarial surface for any
consumer that lets it influence ranking. Recommended posture (as implemented
by Beacon, the reference consumer):

- **Cap the schema bonus.** Presence/completeness of a head block should be a
  bounded boost, never a dominant term — a stuffed head block must not beat
  genuine text relevance.
- **Date sanity.** Ignore `date`/`published`/`updated` values in the future or
  implausibly old; fall back to crawl-observed times (first seen / content
  last changed). Declared dates refine recency; they must not fabricate it.
- **Type cross-check.** If the declared `type` wildly contradicts the page's
  inferred shape, rank by the inferred type (still display the declared one).
  Declaration is a hint, not an assertion.
- **`canonical` is for dedupe.** Pages sharing a `canonical` value are one
  logical document — collapse them in results (mirrors are common on the
  mesh); attribute to the best-ranked copy.
- MeshData remains **inert** (§4): none of this changes rendering; it only
  bounds how much machine trust the block earns.
