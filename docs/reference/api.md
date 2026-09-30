# Python API reference

The import namespace is `pygeocdse`. CQL2 JSON inputs may be Python dictionaries or JSON strings unless otherwise stated.

## Filter translation: `pygeocdse.evaluator`

| Callable | Result and behavior |
| --- | --- |
| `to_cdse(cql2_filter)` | Returns an OData filter string using identity field mapping. Parses CQL2 JSON; does not send a request. |
| `to_cdse_where(root, field_mapping, function_map=None)` | Evaluates a pygeofilter AST and returns a string. `field_mapping` maps attribute names; `function_map` maps function names and defaults to an empty mapping. |
| `CDSEEvaluator(attribute_map, function_map)` | AST evaluator used by both translation functions. |
| `http_invoke(base_url, cql2_filter, limit=20, max_items=200, timeout=30)` | Returns the decoded OData response mapping from one GET request. |

`http_invoke` appends `$filter`, `$top=max_items`, and expansions for `Assets`, `Attributes`, and `Locations`. It sends `Prefer: odata.maxpagesize=<limit>` and passes `timeout` in seconds to HTTPX. Supply a Products endpoint without an existing query string. It calls `raise_for_status()` and does not follow pagination links. HTTPX connection, timeout, status, and JSON decoding errors can propagate.

Unknown query attributes raise `ValueError`. Missing field/function mappings can raise `KeyError`. A custom field mapping does not replace the built-in type registry: comparison type lookup uses the original attribute name. See [operators](operators.md) and [attributes](../attributes.md).

## AST helpers: `pygeocdse.ast_utils`

Each helper accepts an existing AST or `None`, returns an AST, and combines new constraints with an existing filter using AND.

| Signature | Constraint |
| --- | --- |
| `collections_filter(filter, collections)` | OR of `Collection/Name` equalities. Strips names and discards blanks; raises `ValueError` when none remain. |
| `bbox_filter(filter, bbox)` | Spatial intersection with a box `(min_lon, min_lat, max_lon, max_lat)`. |
| `datetime_or_interval_filter(filter, datetime)` | Single value: `ContentDate/Start >= value`. Closed `start/end`: start >= lower bound AND end <= upper bound. |

Empty datetime strings and missing interval endpoints raise `ValueError`. Open-ended intervals are not supported by this helper.

## STAC conversion: `pygeocdse.converters.odata2stac`

| Signature | Return |
| --- | --- |
| `odata_products_to_stac_item_collection(url, odata)` | `pystac.ItemCollection` |
| `to_stac_item_collection(url, odata, output_stream)` | `None`; writes indented JSON to a text stream |

`odata` is a response mapping with a `value` array. `url` is used in derived-from links. No pagination link is copied. Products without footprints are skipped; unsupported footprint geometry types and missing `beginningDateTime` raise `ValueError`. Mapping handlers can also raise on missing companion attributes or invalid enum values. See the [STAC crosswalk](../odata-stac-crosswalk.md).

## GeoJSON conversion: `pygeocdse.converters.odata2geojson`

| Signature | Return |
| --- | --- |
| `odata_products_to_feature_collection_geojson(odata, opts=DEFAULT_FEATURE_BUILD_OPTIONS)` | `geojson.FeatureCollection` |
| `to_feature_collection_geojson(odata, output_stream, opts=DEFAULT_FEATURE_BUILD_OPTIONS)` | `None`; writes indented JSON to a text stream |

`FeatureBuildOptions` is a frozen dataclass:

| Field | Default | Meaning |
| --- | --- | --- |
| `feature_id_getter` | Function returning product `Id` | Callable receiving a product dictionary |
| `include_bbox` | `True` | Include per-feature and aggregate bounding boxes; supports Polygon/MultiPolygon |
| `property_filter` | `None` | Optional `(name, value) -> bool` callable selecting properties |

Properties are `id`, `name`, `content_start`, `content_end`, `origin_date`, `publication_date`, `modification_date`, `online`, `s3_path`, `content_type`, `content_length`, and `checksum`. Values equal to `None` are omitted. Dates are parsed with `datetime.fromisoformat` and serialized with `isoformat`. Products without geometry are skipped. A response `@odata.nextLink` becomes the top-level non-standard `next` member.
