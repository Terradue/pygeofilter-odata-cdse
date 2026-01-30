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

from dataclasses import dataclass
from datetime import datetime
from loguru import logger
from pystac import (
    Asset,
    Item,
    ItemCollection,
    Link,
    RelType
)
from pystac.extensions.processing import ProcessingExtension
from pystac.extensions.product import ProductExtension
from pystac.extensions.sar import (
    Polarization,
    SarExtension
)
from pystac.extensions.sat import (
    OrbitState,
    SatExtension
)
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Protocol,
    TextIO
)

import json

def _parse_rfc3339(dt: str) -> datetime:
    """Parse timestamps like '2025-01-28T15:50:03.000000Z' into aware datetime."""
    if dt.endswith("Z"):
        dt = dt[:-1] + "+00:00"
    return datetime.fromisoformat(dt)

# Handlers

class Handler(Protocol):
    def __call__(self, value: Any, target_item: Item) -> None: ...


def _set_date(
    target_property: str,
    value: Any,
    target_item: Item
):
    target_item.properties[target_property] = _parse_rfc3339(str(value)).isoformat()


def on_beginning_datetime(
    value: Any,
    target_item: Item
):
    _set_date("start_datetime", value, target_item)


def on_ending_datetime(
    value: Any,
    target_item: Item
):
    _set_date("end_datetime", value, target_item)


def on_orbit_number(
    value: Any,
    target_item: Item
):
    SatExtension.ensure_has_extension(target_item, add_if_missing=True)
    target_item.ext.sat.absolute_orbit=value

def on_relative_orbit_number(
    value: Any,
    target_item: Item
):
    SatExtension.ensure_has_extension(target_item, add_if_missing=True)
    target_item.ext.sat.relative_orbit=value

def on_orbit_direction(
    value: Any,
    target_item: Item
):
    SatExtension.ensure_has_extension(target_item, add_if_missing=True)
    target_item.ext.sat.orbit_state=OrbitState[str(value).upper()]

def on_polarisation_channels(
    value: Any,
    target_item: Item
):
    SarExtension.ensure_has_extension(target_item, add_if_missing=True)
    target_item.ext.sar.polarizations = [Polarization[name] for name in str(value).split("&")]

def on_product_type(
    value: Any,
    target_item: Item
):
    product_ext = ProductExtension.ext(target_item, add_if_missing=True)
    product_ext.product_type = value

def on_timeliness(
    value: Any,
    target_item: Item
):
    product_ext = ProductExtension.ext(target_item, add_if_missing=True)
    product_ext.apply(
        timeliness_category = value,
        timeliness = "N/A"
    )

def on_processing_center(
    value: Any,
    target_item: Item
):
    proc_ext = ProcessingExtension.ext(target_item, add_if_missing=True)
    proc_ext.facility = value

def on_processing_level(
    value: Any,
    target_item: Item
):
    proc_ext = ProcessingExtension.ext(target_item, add_if_missing=True)
    proc_ext.level = value

def on_processing_date(
    value: Any,
    target_item: Item
):
    proc_ext = ProcessingExtension.ext(target_item, add_if_missing=True)
    proc_ext.processing_datetime = _parse_rfc3339(str(value))

def on_processor_name(
    value: Any,
    target_item: Item
):
    proc_ext = ProcessingExtension.ext(target_item, add_if_missing=True)
    proc_ext.software = value

def on_processor_version(
    value: Any,
    target_item: Item
):
    proc_ext = ProcessingExtension.ext(target_item, add_if_missing=True)
    proc_ext.version = value

DISPATCH_REGISTRY: Dict[str, Handler] = {
    "beginningDateTime": on_beginning_datetime,
    "endingDateTime": on_ending_datetime,
    "orbitNumber": on_orbit_number,
    "relativeOrbitNumber": on_relative_orbit_number,
    "orbitDirection": on_orbit_direction,
    "polarisationChannels": on_polarisation_channels,
    "productType": on_product_type,
    "timeliness": on_timeliness,
    "processingCenter": on_processing_center,
    "processingLevel": on_processing_level,
    "processingDate": on_processing_date,
    "processorName": on_processor_name,
    "processorVersion": on_processor_version
}

# Convert

def _bbox_from_geojson_geometry(geom: Dict[str, Any]) -> List[float]:
    """
    Compute [minx, miny, maxx, maxy] from a GeoJSON geometry.
    Supports Polygon and MultiPolygon.
    """
    gtype = geom.get("type")
    coords = geom.get("coordinates")

    def iter_points_polygon(poly_coords):
        for ring in poly_coords:
            for x, y in ring:
                yield x, y

    def iter_points_multipolygon(mpoly_coords):
        for poly in mpoly_coords:
            yield from iter_points_polygon(poly)

    if gtype == "Polygon":
        pts = list(iter_points_polygon(coords))
    elif gtype == "MultiPolygon":
        pts = list(iter_points_multipolygon(coords))
    else:
        raise ValueError(f"Unsupported geometry type: {gtype}")

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return [min(xs), min(ys), max(xs), max(ys)]


def odata_products_to_stac_item_collection(
    url: str,
    odata: Mapping[str, Any]
) -> ItemCollection:
    """
    Convert an OData Products response to a PySTAC ItemCollection.

    Expected input shape:
      { "value": [ {product}, ... ], "@odata.nextLink": ... }
    """
    products: List[Dict[str, Any]] = list(odata.get("value") or [])

    logger.debug(f"Processing {len(products)} Product(s).")

    items: List[Item] = []

    for i, product in enumerate(products):
        logger.debug("------------------------------------------------------------------------")
        logger.debug(f"Processing Product {i + 1} of {len(products)}")

        geom = product.get("GeoFootprint")
        if not geom:
            logger.warning(f"Product {i + 1} of {len(products)} with ID '{product.get('Id')}' does not declare the 'GeoFootprint' field, skipping it.")
            # Skip products without geometry (or raise if you prefer)
            continue

        bbox = _bbox_from_geojson_geometry(geom)

        dt = _parse_rfc3339(str(product.get("OriginDate")))

        properties: dict[str, Any] = {}

        item: Item = Item(
            id=str(product.get('Id')),
            geometry=geom,
            bbox=bbox,
            datetime=dt,
            properties=properties
        )

        item.add_link(
            Link(
                rel=RelType.DERIVED_FROM,
                target=f"{url}?$filter=Name%20eq%20%27{product.get('Name')}%27&$expand=Assets&$expand=Attributes#OData.CSC.StringAttribute",
                media_type="application/json",
                title="OData product entry"
            )
        )

        locations = product.get("Locations") or []
        if locations:
            for location in locations:
                asset = Asset(
                    href=str(location.get("DownloadLink")),
                    # media_type=product.get("ContentType") or product.get("@odata.mediaContentType"),
                    roles=["data"],
                    title=str(location.get("FormatType")),
                    extra_fields={
                        "file:size": location.get("ContentLength")
                    },
                )

                checksums = location.get("Checksum") or []
                for checksum in checksums:
                    asset.extra_fields[f"checksum:{checksum.get('Algorithm')}"] = checksum.get("Value")

                item.add_asset(str(location.get("FormatType")), asset)
        else:
            # try guess
            if "S3Path" in product:
                asset = Asset(
                    href=str(product.get("S3Path")),
                    media_type=product.get("ContentType") or product.get("@odata.mediaContentType"),
                    roles=["data"],
                    title=product.get("Name"),
                    extra_fields={
                        "file:size": product.get("ContentLength"),
                        "checksum": product.get("Checksum"),
                    },
                )
                item.add_asset("data", asset)

            # Add the zipped archive
            zip_asset = Asset(
                href=f"https://download.dataspace.copernicus.eu/odata/v1/Products({product.get('Id')})/$value",
                media_type="application/zip",
                roles=[
                    "data",
                    "metadata",
                    "archive"
                ],
                title="application/zip"
            )
            item.add_asset("Product", zip_asset)

        # Add all extra fields
        attributes = product.get("Attributes") or []
        for attribute in attributes:
            name: str = str(attribute.get("Name"))
            value: Any = attribute.get("Value")
            if name in DISPATCH_REGISTRY:
                DISPATCH_REGISTRY[name](value, item)
            else:
                logger.warning(f"Attribute '{name}' not supported yet.")

        logger.debug(f"Appending STAC Item '{item.id}")

        items.append(item)

    return ItemCollection(items, clone_items=True)


def to_stac_item_collection(
    url: str,
    odata: Mapping[str, Any],
    output_stream: TextIO
):
    item_collection: ItemCollection = odata_products_to_stac_item_collection(url, odata)
    json.dump(
        item_collection.to_dict(),
        output_stream,
        indent=2
    )
