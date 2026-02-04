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

from enum import auto, Enum
from loguru import logger
from pathlib import Path
from pygeocdse.evaluator import http_invoke
from pygeocdse.ast_utils import (
    bbox_filter,
    collections_filter,
    datetime_or_interval_filter,
)
from pygeocdse.converters.odata2stac import to_stac_item_collection
from pygeofilter.ast import AstType
from pygeofilter.backends.cql2_json import to_cql2
from pygeofilter.parsers.ecql import parse as parse_ecql
from pygeofilter.parsers.cql2_json import parse as parse_cql2_json
from typing import Any, List, Mapping, Tuple
import click
import requests
import sys


@click.group(
    context_settings={"show_default": True, "help_option_names": ["-h", "--help"]}
)
def main():
    """OData client CLI."""
    pass


class HttpMethod(Enum):
    GET = auto()
    POST = auto()


class FilterLang(Enum):
    CQL2_JSON = "cql2-json"
    CQL2_TEXT = "cql2-text"


@main.command("search")
@click.argument("url", type=click.STRING)
@click.option(
    "-c",
    "--collections",
    multiple=True,
    required=False,
    help="One or more collection IDs.",
)
@click.option(
    "--ids",
    multiple=True,
    required=False,
    type=click.STRING,
    help="One or more Item IDs (ignores other parameters).",
)
@click.option(
    "--bbox",
    type=(click.FLOAT, click.FLOAT, click.FLOAT, click.FLOAT),
    required=False,
    help="Bounding box (min lon, min lat, max lon, max lat).",
)
@click.option(
    "--intersects",
    type=click.STRING,
    required=False,
    help="GeoJSON Feature or geometry (file or string)",
)
@click.option(
    "--datetime",
    type=click.STRING,
    required=False,
    help="Single datetime or begin and end datetime (e.g., 2017-01-01/2017-02-15)",
)
@click.option(
    "--query",
    multiple=True,
    required=False,
    type=click.STRING,
    help="Query properties of form KEY=VALUE (>=, <=, =, <>, >, < supported)",
)
@click.option(
    "--filter",
    type=click.STRING,
    required=False,
    help="Filter on queryables using language specified in filter-lang parameter",
)
@click.option(
    "--filter-lang",
    help="Filter language used within the filter parameter",
    type=click.Choice(
        [FilterLang.CQL2_JSON.value, FilterLang.CQL2_TEXT.value], case_sensitive=False
    ),
    default=FilterLang.CQL2_JSON.value,
)
@click.option(
    "--sortby", help="Sort by fields", type=click.STRING, required=False, multiple=True
)
@click.option(
    "--fields",
    help="Control what fields get returned",
    type=click.STRING,
    required=False,
    multiple=True,
)
@click.option(
    "--limit", help="Page size limit", required=False, type=click.INT, default=20
)
@click.option(
    "--max-items",
    help="Max items to retrieve from search",
    required=False,
    type=click.INT,
    default=200,
)
@click.option(
    "--method",
    type=click.Choice(HttpMethod, case_sensitive=False),
    help="GET or POST",
    required=False,
    default=HttpMethod.POST,
)
@click.option(
    "--save",
    type=click.Path(path_type=Path),
    required=False,
    help="Filename to save GeoJSON FeatureCollection to",
)
def search_cmd(
    url: str,
    collections: List[str] | None,
    ids: List[str] | None,
    bbox: Tuple[float, ...] | None,
    intersects: str | None,
    datetime: str | None,
    query: str | None,
    filter: str | None,
    filter_lang: str | None,
    sortby: List[str] | None,
    fields: List[str] | None,
    limit: int,
    max_items: int,
    method: HttpMethod | None,
    save: Path | None,
):
    try:
        ast: AstType | None = None

        if filter:
            if FilterLang.CQL2_JSON.value == filter_lang:
                ast = parse_cql2_json(filter)
            else:
                ast = parse_ecql(filter)  # type: ignore

        if collections:
            ast = collections_filter(ast, collections)
        if bbox:
            ast = bbox_filter(ast, bbox)
        if datetime:
            ast = datetime_or_interval_filter(ast, datetime)

        if ast is None:
            raise Exception(
                "At least one of the --filter|--collections|--bbox|--datetime option must be set."
            )

        cql2_json_str = to_cql2(ast)
        result: Mapping[str, Any] = http_invoke(
            base_url=url,
            cql2_filter=cql2_json_str,
            limit=limit,
            max_items=max_items
        )

        if save:
            save.parent.mkdir(parents=True, exist_ok=True)
            with save.open("w") as output_stream:
                to_stac_item_collection(url, result, output_stream)
            logger.success(
                f"'Results successfully converted to STAC Item Collection to {save.absolute()}."
            )
        else:
            to_stac_item_collection(url, result, sys.stdout)
            logger.success(
                "Results successfully converted to STAC Item Collection."
            )

        logger.info(
            "------------------------------------------------------------------------"
        )
        logger.success("BUILD SUCCESS")
    except Exception as e:
        logger.info(
            "------------------------------------------------------------------------"
        )
        logger.error("BUILD FAILED")
        logger.error(f"An unexpected error occurred: {e}")
