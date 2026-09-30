# CLI reference

Installing the package provides the `odata-client` executable, backed by the Click group `pygeocdse.cli.main`, with a single `search` command. Use:

```console
odata-client --help
odata-client search --help
```

## Search arguments and active options

`search [OPTIONS] URL` requires a Products endpoint as `URL` and at least one of `--filter`, `--collections`, `--bbox`, or `--datetime`.

| Option | Default | Behavior |
| --- | --- | --- |
| `-c`, `--collections TEXT` | None | Repeatable collection names, combined with OR |
| `--bbox FLOAT FLOAT FLOAT FLOAT` | None | Intersection box: min longitude, min latitude, max longitude, max latitude |
| `--datetime TEXT` | None | Start lower bound, or closed start/end containment interval |
| `--filter TEXT` | None | Filter expression |
| `--filter-lang [cql2-json\|cql2-text]` | `cql2-json` | JSON parser, or the pygeofilter ECQL parser for text |
| `--limit INTEGER` | `20` | OData page-size preference |
| `--max-items INTEGER` | `200` | OData `$top`; does not enable pagination |
| `--timeout INTEGER` | `30` | HTTP timeout in seconds |
| `--save PATH` | None | Write STAC ItemCollection JSON to a file; otherwise standard output |
| `-h`, `--help` | — | Show help |

Collection, bounding-box, and datetime constraints are ANDed with the filter. See [search recipes](how-to/search.md).

## Accepted but unused options

`--ids`, `--intersects`, `--query`, `--sortby`, `--fields`, and `--method` are declared by Click but are not used by `search_cmd`. In particular, IDs do not override other parameters and the request always uses GET, despite the declared `--method` default of POST. Use `--bbox` or a spatial CQL2 filter to constrain geometry.

## Output and errors

The command converts one OData response page to a STAC ItemCollection. It creates the parent directory of `--save` if necessary. Conversion requirements and skipped products are described in the [conversion guide](how-to/convert.md).

The command catches exceptions, logs `BUILD FAILED`, and does not explicitly set a failing exit status. Scripts should not rely solely on the process exit code to detect a failed search; Python callers can use `http_invoke` directly to handle exceptions.
