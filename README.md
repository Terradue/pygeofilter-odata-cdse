# pygeofilter-odata-cdse

Translate CQL2 JSON filters into Copernicus Data Space Ecosystem (CDSE) OData queries, search the Products catalogue, and convert responses to STAC or GeoJSON.

Requires Python 3.10 or later. The distribution name is `pygeofilter-odata-cdse`; the Python import name is `pygeocdse`.

## Installation

```console
python -m pip install pygeofilter-odata-cdse
```

Installing the current source requires Git because its dependencies include a PySTAC fork hosted on GitHub.

## Documentation

Read the [documentation website](https://terradue.github.io/pygeofilter-odata-cdse/) or browse the sources:

- **Tutorial:** [Translate your first filter](docs/tutorials/first-filter.md).
- **How-to guides:** [Search the catalogue](docs/how-to/search.md), [convert responses](docs/how-to/convert.md), and [develop and build documentation](docs/how-to/develop.md).
- **Reference:** [Python API](docs/reference/api.md), [operators](docs/reference/operators.md), [attributes](docs/attributes.md), [CLI](docs/cli.md), and [OData–STAC crosswalk](docs/odata-stac-crosswalk.md).
- **Explanation:** [How translation and conversion work](docs/explanation/architecture.md).

The implementation supports a subset of CQL2 for CDSE. See the reference for current behavior and limitations.

## Container images

The container workflow targets `ghcr.io/terradue/pygeofilter-odata-cdse`:

| Git reference | Image tag |
| --- | --- |
| `develop` | `latest-dev` |
| `main` | `latest` |
| `vX.Y.Z` | `X.Y.Z` |

See [container build details and current limitations](docs/reference/containers.md).

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
