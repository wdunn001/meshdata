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

### Types (a dozen, DC/OG-sized)
`index`, `article`, `blog`, `news`, `wiki`, `profile`, `service`, `file-index`,
`forum`, `status`, `media`, `dataset`, `event`. Each maps to a schema.org type
(see the reference `vocab`), e.g. `article`→`Article`, `profile`→`ProfilePage`,
`service`→`WebAPI`, `file-index`→`DataCatalog`.

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
