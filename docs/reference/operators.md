# Operator reference

This page describes the CDSE evaluator, not full CQL2 or OData conformance. The examples use CQL2 JSON property references such as `{"property": "cloudCover"}`.

## Logical and comparison operators

| CQL2 JSON operator | Output |
| --- | --- |
| `and` | Joins clauses with `and` |
| `or` | Parenthesized clauses joined with `or` |
| `not` | Prefixes the evaluated clause with `NOT` |
| `=`, `eq` | `eq` |
| `<>`, `ne` | `ne` |
| `<`, `lt` | `lt` |
| `<=`, `lte` | `le` |
| `>`, `gt` | `gt` |
| `>=`, `gte` | `ge` |
| `in` | Parenthesized OR of typed attribute equality predicates |

Comparisons expect a property on the left. `Collection/Name` comparisons address the product field directly. Other comparisons look up a type in the [attribute registry](../attributes.md) and generate `Attributes/OData.CSC.<Type>Attribute/any(...)`. For multiple collections, use OR of equalities rather than `in`.

See the [comparison examples notebook](../logical_comparison_op.ipynb).

## Spatial operator

`s_intersects` emits `OData.CSC.Intersects(area=geography'SRID=4326;<WKT>')`. Its geometry argument is GeoJSON converted to WKT using Shapely; coordinates are longitude/latitude. The left-hand property is conventionally `geometry`; the output does not use its name. No other spatial predicate has a dedicated handler.

See the [spatial example notebook](../geographical_op.ipynb).

## Temporal operators

Use temporal predicates for `ContentDate/Start`, `ContentDate/End`, or `PublicationDate`. Bounds below describe timestamp-string and interval inputs.

| Operator | Timestamp | Interval `[start, end]` |
| --- | --- | --- |
| `t_after` | `> timestamp` | `> start AND <= end` |
| `t_before` | `< timestamp` | `>= start AND < end` |
| `t_begins` | `>= timestamp` | `>= start AND <= end` |
| `t_ends` | `<= timestamp` | `>= start AND <= end` |

Timestamps are formatted to second precision with a trailing `Z`. Supply UTC timestamps; formatting does not itself normalize timezone offsets. An interval can contain one ISO 8601 duration: `[start, duration]` adds it to the start, and `[duration, end]` subtracts it from the end. Two durations raise `ValueError`.

See the [temporal examples notebook](../temporal_op.ipynb).

## Additional evaluator handlers

The evaluator also contains handlers for `Between`, `Like`, `IsNull`, arithmetic, and mapped functions. These are implementation facilities, not a guarantee that their output is accepted by CDSE. In particular, `Like` and `IsNull` emit SQL-style syntax, and `Between` emits direct field comparisons rather than typed attribute predicates. Function calls require an explicit `function_map` through `to_cdse_where`.

String literals are surrounded with single quotes without escaping embedded quotes. Boolean literals use Python string formatting. Account for these limits when choosing filter values; successful translation alone does not validate a query against the remote catalogue.
