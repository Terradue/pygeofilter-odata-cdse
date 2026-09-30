# How translation and conversion work

The package connects applications that express filters in CQL2 with the CDSE Products catalogue, whose search interface uses OData. Its scope is the subset needed by the implemented CDSE use cases.

## Translation is separate from execution

`to_cdse` parses CQL2 JSON into a pygeofilter abstract syntax tree. `CDSEEvaluator` walks that tree and produces an OData filter string. Keeping this stage separate lets applications inspect generated filters without network access.

`http_invoke` adds the filter to a Products URL, requests expanded metadata, and returns one decoded response. It does not manage a search session or collect every page. Applications that need complete result sets must handle continuation themselves.

## Why attributes need types

CDSE stores queryable metadata such as `cloudCover` and `productType` in typed attribute collections. A cloud-cover comparison therefore becomes a predicate over `DoubleAttribute` entries rather than a comparison against a top-level `cloudCover` field.

The local Sentinel dictionaries supply these types. Lookup currently checks Sentinel-1, Sentinel-2, Sentinel-3, then Sentinel-5P, independent of the collection being searched. Consequently, the registry describes what the translator recognizes; it does not validate whether a particular collection exposes an attribute. The separate Sentinel-1-RTC dictionary is not registered in that lookup.

`Collection/Name` is handled directly. Temporal predicates also target product date fields directly. These distinctions explain why the filter examples use specific operators for collections and dates.

## Conversion is a separate choice

The HTTP helper returns OData data unchanged. The STAC converter maps selected attributes into STAC core and extension fields, constructs assets, and adds links to the source products. It needs acquisition start metadata and a supported footprint. Unmapped attributes are logged rather than copied into arbitrary STAC properties.

The GeoJSON converter offers a smaller representation: footprints plus a curated set of product properties. It can filter those properties and retain the OData continuation URL in a custom member. Choose it when STAC extension semantics are unnecessary.

The CLI combines filtering, one HTTP request, and STAC conversion. Its interface resembles a STAC search client, but several declared options are unused and it does not implement full STAC API search semantics. Consult the [CLI reference](../cli.md) when deciding whether to use the CLI or compose the Python functions.
