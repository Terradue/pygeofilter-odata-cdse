# Convert an OData response

Use this guide to convert a saved Products response containing a `value` array. Install the package first; conversion itself does not make HTTP requests.

## Write a STAC ItemCollection

Save your OData JSON response as `products.json`, then run:

```python
import json
from pygeocdse.converters.odata2stac import to_stac_item_collection

with open("products.json") as source:
    response = json.load(source)
url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
with open("items.json", "w") as output:
    to_stac_item_collection(url, response, output)
```

For a local example in a checkout, use `tests/artifacts/odata_search.json` as the input file.

Products need a Polygon or MultiPolygon `GeoFootprint` and a `beginningDateTime` attribute. Products without a footprint are skipped; a missing beginning time raises `ValueError`. Include `platformSerialIdentifier` when supplying `platformShortName`. Expand `Attributes` and `Locations` when fetching data; `http_invoke` requests these expansions.

To work with a PySTAC object instead of writing JSON, call `odata_products_to_stac_item_collection(url, response)`. Consult the [crosswalk](../odata-stac-crosswalk.md) for fields and assets. STAC conversion does not preserve the OData next-page link.

## Write a GeoJSON FeatureCollection

Use the GeoJSON converter when you need footprints and curated product fields without STAC extension mapping:

```python
import json
from pygeocdse.converters.odata2geojson import to_feature_collection_geojson

with open("products.json") as source:
    response = json.load(source)
with open("features.json", "w") as output:
    to_feature_collection_geojson(response, output)
```

This converter skips products without footprints and, by default, computes bounding boxes for Polygon and MultiPolygon geometries. It copies `@odata.nextLink` into a non-standard top-level `next` member.

## Select GeoJSON properties

Pass `FeatureBuildOptions` to retain only the properties you need:

```python
from pygeocdse.converters.odata2geojson import (
    FeatureBuildOptions,
    odata_products_to_feature_collection_geojson,
)

options = FeatureBuildOptions(
    include_bbox=False,
    property_filter=lambda name, value: name in {"name", "content_start"},
)
features = odata_products_to_feature_collection_geojson(response, options)
```

See the [Python API reference](../reference/api.md) for defaults and return types.
