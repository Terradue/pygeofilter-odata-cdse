# OData client Command Line Tool

Inspired by the [PySTAC Client](https://pystac-client.readthedocs.io/en/stable/), the module comes with a commodity CLI that reflects the same interfaces.

## Available Commands

```
$ odata-client
Usage: odata-client [OPTIONS] COMMAND [ARGS]...

  OData client CLI.

Options:
  -h, --help  Show this message and exit.

Commands:
  search
```

## Search

```
e$ odata-client search --help
Usage: odata-client search [OPTIONS] URL

Options:
  -c, --collections TEXT          One or more collection IDs.
  --ids TEXT                      One or more Item IDs (ignores other
                                  parameters).
  --bbox <FLOAT FLOAT FLOAT FLOAT>...
                                  Bounding box (min lon, min lat, max lon, max
                                  lat).
  --intersects TEXT               GeoJSON Feature or geometry (file or string)
  --datetime TEXT                 Single datetime or begin and end datetime
                                  (e.g., 2017-01-01/2017-02-15)
  --query TEXT                    Query properties of form KEY=VALUE (>=, <=,
                                  =, <>, >, < supported)
  --filter TEXT                   Filter on queryables using language
                                  specified in filter-lang parameter
  --filter-lang [cql2-json|cql2-text]
                                  Filter language used within the filter
                                  parameter  [default: cql2-json]
  --sortby TEXT                   Sort by fields
  --fields TEXT                   Control what fields get returned
  --limit INTEGER                 Page size limit  [default: 20]
  --max-items INTEGER             Max items to retrieve from search  [default:
                                  200]
  --method [get|post]             GET or POST  [default: POST]
  --save PATH                     Filename to save GeoJSON FeatureCollection
                                  to
  -h, --help                      Show this message and exit.
```

### Example

```
odata-client search \
--filter-lang cql2-json \
--filter '{"op":"and","args":[{"op":"in","args":[{"property":"productType"},["IW_GRHD_1S","IW_GRDH_1S","EW_GRDM_1S","EW_GRDH_1S","S1_GRDH_1S","S2_GRDH_1S","S3_GRDH_1S","S4_GRDH_1S","S5_GRDH_1S","S6_GRDH_1S"]]}]}' \
--collections SENTINEL-1 \
--collections SENTINEL-2 \
--bbox 12.655118166047592 40.35854475076158 28.334291357162826 48.347694733853245 \
--datetime 2023-02-01T00:00:00Z/2023-02-28T23:59:59Z \
--limit 30 \
--save ./test/a/b/c/item_collection.json \
https://catalogue.dataspace.copernicus.eu/odata/v1/Products
```

Results in `./test/a/b/c/item_collection.json` will be saved as [STAC API - ItemCollection Fragment](https://github.com/radiantearth/stac-api-spec/blob/release/v1.0.0/fragments/itemcollection/README.md).
