# Copyright 2025-2026 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from datetime import (
    datetime,
    timezone
)
from pygeofilter.ast import (
    And,
    AstType,
    Attribute,
    Equal,
    GeometryIntersects,
    Or,
    TimeAfter,
    TimeBefore
)
from pygeofilter.parsers.cql2_json import parse as parse_cql2_json
from pygeofilter.util import parse_datetime
from pygeofilter.values import (
    Geometry
)
from shapely.geometry import (
    box,
    mapping
)
from typing import (
    Sequence,
    Tuple
)

def _and_concat(
    left: AstType | None,
    right: AstType
) -> AstType:
    """
    Flatten nested ANDs from `left` and `right`, then rebuild as a left-associated AND chain.

    Assumes `left` and `right` are non-None and already validated as AstType.
    """
    if not left:
        return right

    parts: list[AstType] = []

    def collect(node: AstType) -> None:
        if isinstance(node, And):
            # Guard against unexpected malformed nodes
            lhs = getattr(node, "lhs", None)
            rhs = getattr(node, "rhs", None)
            if lhs is None or rhs is None:
                raise ValueError(f"Malformed And node (missing lhs/rhs): {node!r}")

            collect(lhs)
            collect(rhs)
        else:
            parts.append(node)

    collect(left)
    collect(right)

    # At least two parts exist unless one side was a degenerate And,
    # but keep this safe anyway.
    if not parts:
        raise ValueError("and_concat: no clauses collected (unexpected empty AND tree)")

    expr = parts[0]
    for p in parts[1:]:
        expr = And(expr, p)

    return expr

def collections_filter(
    filter: AstType | None,
    collections: Sequence[str]
) -> AstType:
    """
    Build a pygeofilter AST equivalent to:

      (property_name = c1) OR (property_name = c2) OR ...

    If `collections` has a single item, returns the single "=" expression (not an Or).
    """
    cols = [c.strip() for c in collections if c and c.strip()]
    if not cols:
        raise ValueError("collections_or_ast: `collections` is empty (or only blanks)")

    # property reference and "=" nodes
    prop = Attribute("Collection/Name")
    terms: list[AstType] = [Equal(prop, c) for c in cols]

    if len(terms) == 1:
        return _and_concat(filter, terms[0])

    # left-associative OR chain: Or(Or(t1, t2), t3)...
    expr: AstType = Or(terms[0], terms[1])
    for t in terms[2:]:
        expr = Or(expr, t)

    return _and_concat(filter, expr)

def bbox_filter(
    filter: AstType | None,
    bbox: Tuple[float]
) -> AstType:
    geometry = box(*bbox)

    geometry_filter = GeometryIntersects(
        Attribute("geometry"),
        Geometry(mapping(geometry))
    )

    return _and_concat(filter, geometry_filter)


def _as_utc(
    datetime: str
) -> datetime:
    dt: datetime = parse_datetime(datetime)
    # pygeofilter.util.parse_datetime may return naive or tz-aware dt depending on input
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def datetime_or_interval_filter(
    filter: AstType | None,
    datetime: str
) -> AstType:
    datetime = datetime.strip()
    if not datetime:
        raise ValueError("Empty datetime/interval string")

    if "/" in datetime:
        start_raw, end_raw = (p.strip() for p in datetime.split("/", 1))
        if not start_raw or not end_raw:
            raise ValueError("Both start and end must be provided in 'start/end'")

        datetime_filter = {
            "op": "and",
            "args": [
                {
                    "op": "t_begins",
                    "args": [
                        {"property": "ContentDate/Start"},
                        {"timestamp": start_raw}
                    ]
                },
                {
                    "op": "t_ends",
                    "args": [
                        {"property": "ContentDate/End"},
                        {"timestamp": end_raw}
                    ]
                }
            ]
        }
    else:
        # single instant/date
        datetime_filter = {
            "op": "t_begins",
            "args": [
                {"property": "ContentDate/Start"},
                {"timestamp": datetime}
            ]
        }

    return _and_concat(filter, parse_cql2_json(datetime_filter))
