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


from pygeofilter.ast import (
    And,
    AstType
)
from pygeofilter.parsers.cql2_json import parse as parse_cql2_json
from typing import (
    Any,
    Mapping
)


def and_concat(
    left: AstType,
    right: Mapping[str, Any]
) -> And:
    """
    Parse `right` (CQL2-JSON dict) into an AST, then flatten nested ANDs from `left`
    and that parsed right AST, and rebuild as a left-associated AND chain.

    Returns an `ast.And` (top-level).
    """

    if not isinstance(left, AstType):
        raise TypeError(f"Expected `left` to be ast.AstType, got {type(left)!r}")

    if not isinstance(right, Mapping):
        raise TypeError(f"Expected `right` to be a Mapping[str, Any], got {type(right)!r}")

    right_ast: AstType = parse_cql2_json(dict(right))

    parts: list[AstType] = []

    def collect(node: AstType) -> None:
        if not isinstance(node, AstType):
            raise TypeError(f"Expected ast.AstType, got {type(node)!r}: {node!r}")

        if isinstance(node, And):
            lhs = getattr(node, "lhs", None)
            rhs = getattr(node, "rhs", None)
            if lhs is None or rhs is None:
                raise ValueError(f"Malformed ast.And node (missing lhs/rhs): {node!r}")
            if not isinstance(lhs, AstType) or not isinstance(rhs, AstType):
                raise ValueError(f"Malformed ast.And node (lhs/rhs not AstType): {node!r}")

            collect(lhs)
            collect(rhs)
        else:
            parts.append(node)

    collect(left)
    collect(right_ast)

    if len(parts) < 2:
        # With non-empty left and right this should never happen unless the AST is malformed
        raise ValueError("and_concat: expected at least two clauses after collection")

    expr: AstType = parts[0]
    for p in parts[1:]:
        expr = And(expr, p)

    if not isinstance(expr, And):
        # Defensive: should be impossible with len(parts) >= 2
        raise ValueError("and_concat: expected top-level ast.And after rebuild")

    return expr
