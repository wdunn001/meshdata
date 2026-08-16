# MeshData

A lightweight **"schema.org for micron"**. NomadNet page authors declare a page's
**type** and **metadata** in an invisible `#`-comment head block; crawlers (like
[Beacon](https://github.com/wdunn001/beacon)) read it to categorize pages, show
good result snippets, and rank them. Names mirror schema.org / Dublin Core /
OpenGraph. Part of the MeshAPI family. See [`SPEC.md`](SPEC.md).

```
# +type: article
# +title: Guk Homecoming Arc, Part Three
# +author: wdunn001
# +date: 2026-08-16
# +description: The player is the unknowing second corruption.
# +tags: eqemu, lore, guk
# +section news = latest-headlines
```

Invisible on every NomadNet client (they discard `#` lines), no extra fetch, no
duplication of visible content, tolerant line-scan parsing (a typo drops one line,
never the block). When a page has no MeshData, consumers infer type + title from
the page's shape rather than failing.

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
