# pygeofilter CDSE OData support for CQL2

`pygeocdse` translates CQL2 JSON expressions into OData filters for the Copernicus Data Space Ecosystem Products catalogue. It also provides an HTTP search helper and converters for STAC ItemCollections and GeoJSON FeatureCollections.

## Choose your starting point

| Your goal | Documentation |
| --- | --- |
| Learn by completing a small example | [Tutorial: translate your first filter](tutorials/first-filter.md) |
| Query products from Python or the CLI | [How to search the catalogue](how-to/search.md) |
| Save a catalogue response as STAC or GeoJSON | [How to convert responses](how-to/convert.md) |
| Work on the project or preview these docs | [Development guide](how-to/develop.md) |
| Look up exact behavior | [API](reference/api.md), [operators](reference/operators.md), [attributes](attributes.md), [CLI](cli.md), [STAC crosswalk](odata-stac-crosswalk.md) |
| Understand the design and its limits | [Translation and conversion explained](explanation/architecture.md) |

The documentation follows [Diátaxis](https://diataxis.fr/): tutorials teach through a guided exercise, how-to guides solve specific tasks, reference describes behavior, and explanation gives context.

This project implements a CDSE-focused subset of CQL2. Begin with the offline tutorial; live search examples require network access and their results change with catalogue contents.
