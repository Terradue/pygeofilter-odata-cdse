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

from enum import (
    auto,
    Enum
)
from loguru import logger
from pathlib import Path
from pygeocdse.evaluator import to_cdse
from pygeocdse.converters.odata2stac import to_stac_item_collection
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Tuple
)
import click
import json
import requests
import sys

@click.group(
    context_settings={
        "show_default": True,
        "help_option_names": [
            "-h",
            "--help"
        ]
    }
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


def _parse_bbox(
    _: click.Context,
    __: click.Parameter,
    value: Optional[Tuple[float, ...]]
) -> List[float] | None:
    # Typical STAC bbox: 4 floats
    if value is None:
        return None
    if len(value) !=4:
        raise click.BadParameter("BBox must be 4 numbers (minx miny maxx maxy).")
    return list(value)


@main.command("search")
@click.argument(
    "url",
    type=click.STRING
)
@click.option(
    "-c",
    "--collections",
    multiple=True,
    required=False,
    help="One or more collection IDs."
)
@click.option(
    "--ids",
    multiple=True,
    required=False,
    type=click.STRING,
    help="One or more Item IDs (ignores other parameters)."
)
@click.option(
    "--bbox",
    type=click.FLOAT,
    multiple=True,
    required=False,
    # callback=_parse_bbox,
    help="Bounding box (min lon, min lat, max lon, max lat)."
)
@click.option(
    "--intersects",
    type=click.STRING,
    required=False,
    help="GeoJSON Feature or geometry (file or string)"
)
@click.option(
    "--datetime",
    type=click.STRING,
    required=False,
    help="Single datetime or begin and end datetime (e.g., 2017-01-01/2017-02-15)"
)
@click.option(
    "--query",
    multiple=True,
    required=False,
    type=click.STRING,
    help="Query properties of form KEY=VALUE (>=, <=, =, <>, >, < supported)"
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
        [FilterLang.CQL2_JSON.value, FilterLang.CQL2_TEXT.value],
        case_sensitive=False
    ),
    default=FilterLang.CQL2_JSON.value,
)
@click.option(
    "--sortby",
    help="Sort by fields",
    type=click.STRING,
    required=False,
    multiple=True
)
@click.option(
    "--fields",
    help="Control what fields get returned",
    type=click.STRING,
    required=False,
    multiple=True
)
@click.option(
    "--limit",
    help="Page size limit",
    required=False,
    type=click.INT
)
@click.option(
    "--max-items",
    help="Max items to retrieve from search",
    required=False,
    type=click.INT,
)
@click.option(
    "--method",
    type=click.Choice(
        HttpMethod,
        case_sensitive=False
    ),
    help="GET or POST",
    required=False,
    default=HttpMethod.POST
)
@click.option(
    "--save",
    type=click.Path(
        path_type=Path
    ),
    required=False,
    help="Filename to save GeoJSON FeatureCollection to"
)
def search_cmd(
    url: str,
    collections: Tuple[str],
    ids: Tuple[str],
    bbox: str,
    intersects: str,
    datetime: str,
    query: str,
    filter: str,
    filter_lang: str,
    sortby: Tuple[str],
    fields: Tuple[str],
    limit: int,
    max_items: int,
    method: HttpMethod,
    save: Path | None
):
    try:
        if FilterLang.CQL2_JSON.value == filter_lang:
            cql2_filter = json.loads(filter)
        else:
            cql2_filter = filter
        
        transpiled_filter = to_cdse(cql2_filter)
        filter_url = f"{url}?$filter={transpiled_filter}&$expand=Assets&$expand=Attributes&$expand=Locations"

        logger.debug(f"Invoking {filter_url}...")

        response = requests.get(filter_url)
        response.raise_for_status()
        result: Mapping[str, Any] = response.json()

        if save:
            save.parent.mkdir(parents=True, exist_ok=True)
            with save.open("w") as output_stream:
                to_stac_item_collection(result, output_stream)
            logger.success(f"'{filter_url}' results successfully converted to STAC Item Collection to {save.absolute()}.")
        else:
            to_stac_item_collection(result, sys.stdout)
            logger.success(f"'{filter_url}' results successfully converted to STAC Item Collection.")

        logger.info('------------------------------------------------------------------------')
        logger.success('BUILD SUCCESS')
    except Exception as e:
        logger.info('------------------------------------------------------------------------')
        logger.error('BUILD FAILED')
        logger.error(f"An unexpected error occurred: {e}")
