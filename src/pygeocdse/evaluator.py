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

from builtins import isinstance
from datetime import date, datetime, timedelta
from functools import wraps
from http import HTTPStatus
from httpx import Client, Headers, Request, RequestNotRead, Response
from loguru import logger
from pygeocdse.odata_attributes import get_attribute_type
from pygeofilter import ast, values
from pygeofilter.backends.evaluator import Evaluator, handle
from pygeofilter.parsers.cql2_json import parse as json_parse
from pygeofilter.util import IdempotentDict, parse_datetime
from typing import Any, Dict, Mapping, Optional
import json
import re
import shapely

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


def date_format(date: str | datetime):
    if isinstance(date, str):
        return date_format(parse_datetime(date))

    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


class CDSEEvaluator(Evaluator):
    def __init__(
        self, attribute_map: Mapping[str, str], function_map: Mapping[str, str]
    ):
        self.attribute_map = attribute_map
        self.function_map = function_map

    @handle(ast.Not)
    def not_(self, node, sub):
        return f"NOT {sub}"

    @handle(ast.And)
    def and_combination(self, node, lhs, rhs):
        return f"{lhs} {node.op.value.lower()} {rhs}"

    @handle(ast.Or)
    def or_combination(self, node, lhs, rhs):
        return f"({lhs} {node.op.value.lower()} {rhs})"

    @handle(ast.Comparison, subclasses=True)
    def comparison(self, node, lhs, rhs):
        if "Collection/Name" == node.lhs.name:
            return f"{node.lhs.name} {COMPARISON_OP_MAP.get(node.op)} {rhs}"

        if "Date" in lhs:
            rhs = node.rhs

        attr_type = get_attribute_type(node.lhs.name)
        return f"Attributes/OData.CSC.{attr_type}Attribute/any(att:att/Name eq {lhs} and att/OData.CSC.{attr_type}Attribute/Value {COMPARISON_OP_MAP[node.op]} {rhs})"

    @handle(ast.Between)
    def between(self, node, lhs, low, high):
        low = low.replace("'", "")
        high = high.replace("'", "")

        inner_lhs = ast.Comparison(node.lhs, low)
        inner_lhs.op = ast.ComparisonOp.GE

        inner_rhs = ast.Comparison(node.lhs, high)
        inner_rhs.op = ast.ComparisonOp.LE

        return f"{inner_lhs.lhs.name} {COMPARISON_OP_MAP.get(inner_lhs.op)} {inner_lhs.rhs} and {inner_rhs.lhs.name} {COMPARISON_OP_MAP.get(inner_rhs.op)} {inner_rhs.rhs}"

    @handle(ast.Like)
    def like(self, node, lhs):
        pattern = node.pattern
        if node.wildcard != "%":
            # TODO: not preceded by escapechar
            pattern = pattern.replace(node.wildcard, "%")
        if node.singlechar != "_":
            # TODO: not preceded by escapechar
            pattern = pattern.replace(node.singlechar, "_")

        # TODO: handle node.nocase
        return (
            f"{lhs} {'NOT ' if node.not_ else ''}LIKE "
            f"'{pattern}' ESCAPE '{node.escapechar}'"
        )

    @handle(ast.In)
    def in_(self, node, lhs, *options):
        attr_type = get_attribute_type(node.lhs.name)

        def _mapper(rhs):
            return f"Attributes/OData.CSC.{attr_type}Attribute/any(att:att/Name eq {lhs} and att/OData.CSC.{attr_type}Attribute/Value eq {rhs})"

        return "(" + " or ".join(map(_mapper, options)) + ")"

    @handle(ast.IsNull)
    def null(self, node, lhs):
        return f"{lhs} IS {'NOT ' if node.not_ else ''}NULL"

    """
    Time comparison handling
    """

    @handle(ast.TimeAfter)
    def timeAfter(self, node, lhs, rhs):
        if isinstance(rhs, values.Interval):
            return f"{node.lhs.name} gt {date_format(rhs.start)} and {node.lhs.name} le {date_format(rhs.end)}"

        if isinstance(rhs, str):
            return f"{node.lhs.name} gt {date_format(rhs)}"

        return f"{node.lhs.name} lt {rhs}"

    @handle(ast.TimeBefore)
    def timeBefore(self, node, lhs, rhs):
        if isinstance(rhs, values.Interval):
            return f"{node.lhs.name} ge {date_format(rhs.start)} and {node.lhs.name} lt {date_format(rhs.end)}"

        if isinstance(rhs, str):
            return f"{node.lhs.name} lt {date_format(rhs)}"

        return f"{node.lhs.name} lt {rhs}"

    @handle(ast.TimeBegins)
    def timeBegin(self, node, lhs, rhs):
        if isinstance(rhs, values.Interval):
            return f"{node.lhs.name} ge {date_format(rhs.start)} and {node.lhs.name} le {date_format(rhs.end)}"

        if isinstance(rhs, str):
            return f"{node.lhs.name} ge {date_format(rhs)}"

        return f"{node.lhs.name} ge {rhs}"

    @handle(ast.TimeEnds)
    def timeEnds(self, node, lhs, rhs):
        if isinstance(rhs, values.Interval):
            return f"{node.lhs.name} ge {date_format(rhs.start)} and {node.lhs.name} le {date_format(rhs.end)}"

        if isinstance(rhs, str):
            return f"{node.lhs.name} le {date_format(rhs)}"

        return f"{node.lhs.name} le {rhs}"

    @handle(values.Interval)
    def interval(self, node, start, end):
        if isinstance(node.start, timedelta) and isinstance(node.end, timedelta):
            raise ValueError(
                f"Both 'start' {start} and 'end' {end} parameters cannot be time deltas"
            )

        if isinstance(node.start, timedelta):
            return values.Interval(node.end - node.start, node.end)
        elif isinstance(node.end, timedelta):
            return values.Interval(node.start, node.start + node.end)
        else:
            return node

    """
    Spatial comparison handling
    """

    @handle(ast.GeometryIntersects, subclasses=True)
    def geometry_intersects(self, node, lhs, rhs):
        return f"OData.CSC.Intersects(area=geography'SRID=4326;{rhs}')"

    @handle(values.Geometry)
    def geometry(self, node: values.Geometry):
        jeometry = json.dumps(node.geometry)
        geometry = shapely.from_geojson(jeometry)
        return str(geometry)

    @handle(ast.Attribute)
    def attribute(self, node: ast.Attribute):
        return f"'{self.attribute_map[node.name]}'"

    @handle(ast.Arithmetic, subclasses=True)
    def arithmetic(self, node: ast.Arithmetic, lhs, rhs):
        op = ARITHMETIC_OP_MAP[node.op]
        return f"({lhs} {op} {rhs})"

    @handle(ast.Function)
    def function(self, node, *arguments):
        func = self.function_map[node.name]
        return f"{func}({','.join(arguments)})"

    @handle(*values.LITERALS)
    def literal(self, node):
        if isinstance(node, str):
            return f"'{node}'"
        elif (isinstance(node, date) or isinstance(node, datetime)) and not isinstance(
            node, timedelta
        ):
            return date_format(node)
        else:
            # TODO:
            return str(node)


def to_cdse(cql2_filter: str | Dict[str, Any]) -> str:
    return to_cdse_where(json_parse(cql2_filter), IdempotentDict())


def to_cdse_where(
    root: ast.AstType,
    field_mapping: Mapping[str, str],
    function_map: Optional[Mapping[str, str]] = None,
) -> str:
    return CDSEEvaluator(field_mapping, function_map or {}).evaluate(root)


def _decode(value):
    if not value:
        return ""

    if isinstance(value, str):
        return value

    return value.decode("utf-8")


def _log_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
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


def _log_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
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
                f"A server error occurred when invoking {kwargs['method'].upper()} {kwargs['url']}, read the logs for details"
            )
        return response

    return wrapper


def http_invoke(
    base_url: str,
    cql2_filter: str | Dict[str, Any],
    limit: int = 20,
    max_items: int = 200,
) -> Mapping[str, Any]:
    current_filter: str = to_cdse(cql2_filter)
    url: str = f"{base_url}?$filter={current_filter}&$top={max_items}&$expand=Assets&$expand=Attributes&$expand=Locations"

    with Client() as http_client:
        http_client.build_request = _log_request(http_client.build_request)  # type: ignore
        http_client.request = _log_response(http_client.request)  # type: ignore
        response: Response = http_client.get(
            url=url, headers={"Prefer": f"odata.maxpagesize={limit}"}, timeout=30
        )

    response.raise_for_status()  # Raise an error for HTTP error codes
    data = response.json()

    return data
