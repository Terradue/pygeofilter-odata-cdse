# Search the CDSE catalogue

Use this guide when you have installed the package and want to retrieve products. See the [tutorial](../tutorials/first-filter.md) for installation and a first translation exercise.

## Search from Python

Pass a CQL2 JSON dictionary and the Products endpoint to `http_invoke`:

```python
from pygeocdse.evaluator import http_invoke

url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
query = {
    "op": "and",
    "args": [
        {"op": "=", "args": [{"property": "Collection/Name"}, "SENTINEL-2"]},
        {"op": "<=", "args": [{"property": "cloudCover"}, 20]},
    ],
}
response = http_invoke(url, query, limit=10, max_items=10, timeout=60)
for product in response.get("value", []):
    print(product["Id"], product["Name"])
```

The returned mapping is the raw OData response. `limit` sets a page-size preference and `max_items` sets `$top`; the helper makes one GET request and does not follow `@odata.nextLink`. Retain that field if your application needs to request subsequent pages.

## Add collection, area, and time constraints

Use the AST helpers to combine constraints, then serialize back to CQL2 JSON:

```python
from pygeofilter.backends.cql2_json import to_cql2
from pygeocdse.ast_utils import (
    bbox_filter,
    collections_filter,
    datetime_or_interval_filter,
)
from pygeocdse.evaluator import to_cdse

ast = collections_filter(None, ["SENTINEL-2"])
ast = bbox_filter(ast, (12.0, 40.0, 15.0, 43.0))
ast = datetime_or_interval_filter(
    ast, "2023-02-01T00:00:00Z/2023-02-28T23:59:59Z"
)
query = to_cql2(ast)
print(to_cdse(query))
```

Send `query` with `http_invoke` as above. Bounding-box coordinates are minimum longitude, minimum latitude, maximum longitude, maximum latitude. The interval requires product start at or after its lower bound and product end at or before its upper bound. A single date/time instead sets a lower bound on product start. Use explicit UTC timestamps ending in `Z`.

## Search from the command line

Use the `odata-client` command installed with the package:

```console
odata-client search \
  --collections SENTINEL-2 \
  --bbox 12 40 15 43 \
  --datetime 2023-02-01T00:00:00Z/2023-02-28T23:59:59Z \
  --limit 10 --max-items 10 \
  --save items.json \
  https://catalogue.dataspace.copernicus.eu/odata/v1/Products
```

This writes a STAC ItemCollection to `items.json`, creating parent directories as needed. Omit `--save` to write JSON to standard output. See [CLI reference](../cli.md) for implemented options and limitations, and [conversion requirements](convert.md) if conversion fails.
