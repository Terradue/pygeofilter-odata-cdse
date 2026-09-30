# Copyright 2025 Terradue
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

import json
import re
from datetime import date, timedelta
from functools import wraps
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar, cast

import shapely
from httpx import Client, Headers, Request, RequestNotRead, Response
from loguru import logger
from pygeofilter import ast, values
from pygeofilter.backends.evaluator import Evaluator
from pygeofilter.backends.evaluator import handle as _handle
from pygeofilter.parsers.cql2_json import parse as json_parse
from pygeofilter.util import IdempotentDict, parse_datetime

from pygeocdse.odata_attributes import get_attribute_type

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

P = ParamSpec("P")
T = TypeVar("T")


def handle(
    *node_classes: type, subclasses: bool = False
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Preserve handler signatures across pygeofilter's untyped decorator."""
    return cast(
        "Callable[[Callable[P, T]], Callable[P, T]]", _handle(*node_classes, subclasses=subclasses)
    )


COMPARISON_OP_MAP = {
    ast.ComparisonOp.EQ: "eq",
    ast.ComparisonOp.NE: "ne",
    ast.ComparisonOp.LT: "lt",
    ast.ComparisonOp.LE: "le",
    ast.ComparisonOp.GT: "gt",
    ast.ComparisonOp.GE: "ge",
}

ARITHMETIC_OP_MAP = {
    ast.ArithmeticOp.ADD: "+",
    ast.ArithmeticOp.SUB: "-",
    ast.ArithmeticOp.MUL: "*",
    ast.ArithmeticOp.DIV: "/",
}


def date_format(value: str | date | timedelta | None) -> str:
    if isinstance(value, str):
        return date_format(parse_datetime(value))
    if not isinstance(value, date):
        raise ValueError("A concrete date is required")
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


class CDSEEvaluator(Evaluator):
    def __init__(self, attribute_map: Mapping[str, str], function_map: Mapping[str, str]) -> None:
        self.attribute_map = attribute_map
        self.function_map = function_map

    @handle(ast.Not)
    def not_(self, node: ast.Not, sub: str) -> str:
        return f"NOT {sub}"

    @handle(ast.And)
    def and_combination(self, node: ast.And, lhs: str, rhs: str) -> str:
        return f"{lhs} {node.op.value.lower()} {rhs}"

    @handle(ast.Or)
    def or_combination(self, node: ast.Or, lhs: str, rhs: str) -> str:
        return f"({lhs} {node.op.value.lower()} {rhs})"

    @handle(ast.Comparison, subclasses=True)
    def comparison(self, node: ast.Comparison, lhs: str, rhs: str) -> str:
        if cast("ast.Attribute", node.lhs).name == "Collection/Name":
            return f"{cast('ast.Attribute', node.lhs).name} {COMPARISON_OP_MAP.get(node.op)} {rhs}"

        if "Date" in lhs:
            rhs = str(node.rhs)

        attr_type = get_attribute_type(cast("ast.Attribute", node.lhs).name)
        return f"Attributes/OData.CSC.{attr_type}Attribute/any(att:att/Name eq {lhs} and att/OData.CSC.{attr_type}Attribute/Value {COMPARISON_OP_MAP[node.op]} {rhs})"

    @handle(ast.Between)
    def between(self, node: ast.Between, lhs: str, low: str, high: str) -> str:
        low = low.replace("'", "")
        high = high.replace("'", "")

        inner_lhs = ast.GreaterEqual(node.lhs, low)

        inner_rhs = ast.LessEqual(node.lhs, high)

        return f"{cast('ast.Attribute', inner_lhs.lhs).name} {COMPARISON_OP_MAP.get(inner_lhs.op)} {inner_lhs.rhs} and {cast('ast.Attribute', inner_rhs.lhs).name} {COMPARISON_OP_MAP.get(inner_rhs.op)} {inner_rhs.rhs}"

    @handle(ast.Like)
    def like(self, node: ast.Like, lhs: str) -> str:
        pattern = cast("str", node.pattern)
        if node.wildcard != "%":
            # TODO: not preceded by escapechar
            pattern = pattern.replace(node.wildcard, "%")
        if node.singlechar != "_":
            # TODO: not preceded by escapechar
            pattern = pattern.replace(node.singlechar, "_")

        # TODO: handle node.nocase
        return f"{lhs} {'NOT ' if node.not_ else ''}LIKE '{pattern}' ESCAPE '{node.escapechar}'"

    @handle(ast.In)
    def in_(self, node: ast.In, lhs: str, *options: str) -> str:
        attr_type = get_attribute_type(cast("ast.Attribute", node.lhs).name)

        def _mapper(rhs: str) -> str:
            return f"Attributes/OData.CSC.{attr_type}Attribute/any(att:att/Name eq {lhs} and att/OData.CSC.{attr_type}Attribute/Value eq {rhs})"

        return "(" + " or ".join(map(_mapper, options)) + ")"

    @handle(ast.IsNull)
    def null(self, node: ast.IsNull, lhs: str) -> str:
        return f"{lhs} IS {'NOT ' if node.not_ else ''}NULL"

    """
    Time comparison handling
    """

    @handle(ast.TimeAfter)
    def timeAfter(self, node: ast.TimeAfter, lhs: str, rhs: object) -> str:
        if isinstance(rhs, values.Interval):
            return f"{cast('ast.Attribute', node.lhs).name} gt {date_format(rhs.start)} and {cast('ast.Attribute', node.lhs).name} le {date_format(rhs.end)}"

        if isinstance(rhs, str):
            return f"{cast('ast.Attribute', node.lhs).name} gt {date_format(rhs)}"

        return f"{cast('ast.Attribute', node.lhs).name} lt {rhs}"

    @handle(ast.TimeBefore)
    def timeBefore(self, node: ast.TimeBefore, lhs: str, rhs: object) -> str:
        if isinstance(rhs, values.Interval):
            return f"{cast('ast.Attribute', node.lhs).name} ge {date_format(rhs.start)} and {cast('ast.Attribute', node.lhs).name} lt {date_format(rhs.end)}"

        if isinstance(rhs, str):
            return f"{cast('ast.Attribute', node.lhs).name} lt {date_format(rhs)}"

        return f"{cast('ast.Attribute', node.lhs).name} lt {rhs}"

    @handle(ast.TimeBegins)
    def timeBegin(self, node: ast.TimeBegins, lhs: str, rhs: object) -> str:
        if isinstance(rhs, values.Interval):
            return f"{cast('ast.Attribute', node.lhs).name} ge {date_format(rhs.start)} and {cast('ast.Attribute', node.lhs).name} le {date_format(rhs.end)}"

        if isinstance(rhs, str):
            return f"{cast('ast.Attribute', node.lhs).name} ge {date_format(rhs)}"

        return f"{cast('ast.Attribute', node.lhs).name} ge {rhs}"

    @handle(ast.TimeEnds)
    def timeEnds(self, node: ast.TimeEnds, lhs: str, rhs: object) -> str:
        if isinstance(rhs, values.Interval):
            return f"{cast('ast.Attribute', node.lhs).name} ge {date_format(rhs.start)} and {cast('ast.Attribute', node.lhs).name} le {date_format(rhs.end)}"

        if isinstance(rhs, str):
            return f"{cast('ast.Attribute', node.lhs).name} le {date_format(rhs)}"

        return f"{cast('ast.Attribute', node.lhs).name} le {rhs}"

    @handle(values.Interval)
    def interval(self, node: values.Interval, start: str, end: str) -> values.Interval:
        if isinstance(node.start, timedelta) and isinstance(node.end, timedelta):
            raise ValueError(
                f"Both 'start' {start} and 'end' {end} parameters cannot be time deltas"
            )

        if isinstance(node.start, timedelta):
            if not isinstance(node.end, date):
                raise ValueError("An interval with a start duration requires an end date")
            return values.Interval(node.end - node.start, node.end)
        if isinstance(node.end, timedelta):
            if not isinstance(node.start, date):
                raise ValueError("An interval with an end duration requires a start date")
            return values.Interval(node.start, node.start + node.end)
        return node

    """
    Spatial comparison handling
    """

    @handle(ast.GeometryIntersects, subclasses=True)
    def geometry_intersects(self, node: ast.GeometryIntersects, lhs: str, rhs: str) -> str:
        return f"OData.CSC.Intersects(area=geography'SRID=4326;{rhs}')"

    @handle(values.Geometry)
    def geometry(self, node: values.Geometry) -> str:
        jeometry = json.dumps(node.geometry)
        geometry = shapely.from_geojson(jeometry)
        return str(geometry)

    @handle(ast.Attribute)
    def attribute(self, node: ast.Attribute) -> str:
        return f"'{self.attribute_map[node.name]}'"

    @handle(ast.Arithmetic, subclasses=True)
    def arithmetic(self, node: ast.Arithmetic, lhs: str, rhs: str) -> str:
        op = ARITHMETIC_OP_MAP[node.op]
        return f"({lhs} {op} {rhs})"

    @handle(ast.Function)
    def function(self, node: ast.Function, *arguments: str) -> str:
        func = self.function_map[node.name]
        return f"{func}({','.join(arguments)})"

    @handle(*values.LITERALS)
    def literal(self, node: object) -> str:
        if isinstance(node, str):
            return f"'{node}'"
        if isinstance(node, date):
            return date_format(node)
        # TODO:
        return str(node)


def to_cdse(cql2_filter: str | dict[str, Any]) -> str:
    return to_cdse_where(json_parse(cql2_filter), IdempotentDict())


def to_cdse_where(
    root: ast.AstType,
    field_mapping: Mapping[str, str],
    function_map: Mapping[str, str] | None = None,
) -> str:
    return cast("str", CDSEEvaluator(field_mapping, function_map or {}).evaluate(root))


def _decode(value: str | bytes | None) -> str:
    if not value:
        return ""

    if isinstance(value, str):
        return value

    return value.decode("utf-8")


def _log_request(func: Callable[P, Request]) -> Callable[P, Request]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Request:
        request: Request = func(*args, **kwargs)

        logger.warning(f"{request.method} {request.url}")

        headers: Headers = request.headers
        for name, value in headers.raw:
            header_value = re.sub(
                r"(\bBearer\s+)[^\s]+",
                r"\1********",
                _decode(value),
                flags=re.IGNORECASE,
            )
            logger.warning(f"> {_decode(name)}: {header_value}")

        logger.warning(">")
        try:
            if request.content:
                logger.warning(_decode(request.content))
        except RequestNotRead:
            logger.warning("[REQUEST BUILT FROM STREAM, OMISSING]")

        return request

    return wrapper


def _log_response(func: Callable[P, Response]) -> Callable[P, Response]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Response:
        response: Response = func(*args, **kwargs)

        if HTTPStatus.MULTIPLE_CHOICES._value_ <= response.status_code:
            log = logger.error
        else:
            log = logger.success

        status: HTTPStatus = HTTPStatus(response.status_code)
        log(f"< {status._value_} {status.phrase}")

        headers: Mapping[str, str] = response.headers
        for name, value in headers.items():
            log(f"< {_decode(name)}: {_decode(value)}")

        log("")

        if response.content:
            log(_decode(response.content))

        if HTTPStatus.MULTIPLE_CHOICES._value_ <= response.status_code:
            raise RuntimeError(
                f"A server error occurred when invoking {str(kwargs['method']).upper()} {kwargs['url']}, read the logs for details"
            )
        return response

    return wrapper


def http_invoke(
    base_url: str,
    cql2_filter: str | dict[str, Any],
    limit: int = 20,
    max_items: int = 200,
    timeout: int = 30,
) -> Mapping[str, Any]:
    current_filter: str = to_cdse(cql2_filter)
    url: str = f"{base_url}?$filter={current_filter}&$top={max_items}&$expand=Assets&$expand=Attributes&$expand=Locations"

    with Client() as http_client:
        http_client.build_request = _log_request(http_client.build_request)  # type: ignore
        http_client.request = _log_response(http_client.request)  # type: ignore
        response: Response = http_client.get(
            url=url, headers={"Prefer": f"odata.maxpagesize={limit}"}, timeout=timeout
        )

    response.raise_for_status()  # Raise an error for HTTP error codes
    return cast("Mapping[str, Any]", response.json())
