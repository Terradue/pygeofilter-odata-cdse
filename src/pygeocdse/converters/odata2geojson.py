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
from typing import Any, Callable, Dict, List, Mapping, TextIO, Optional
import geojson


def _parse_rfc3339(dt: Optional[str]) -> Optional[str]:
    """Normalize timestamps like '2025-01-28T15:50:03.000000Z' to RFC3339."""
    if not dt:
        return None
    if dt.endswith("Z"):
        dt = dt[:-1] + "+00:00"
    return datetime.fromisoformat(dt).isoformat()


def _bbox_from_geojson_geometry(geom: Dict[str, Any]) -> List[float]:
    """Compute [minx, miny, maxx, maxy] from Polygon/MultiPolygon GeoJSON geometry."""
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


def _to_geojson_instance(obj: Dict[str, Any]) -> Any:
    """
    Convert a plain dict (already shaped like GeoJSON) into a geojson.* object.
    geojson.dumps/loads are wrappers around json that return geojson objects. :contentReference[oaicite:2]{index=2}
    """
    return geojson.loads(geojson.dumps(obj))


@dataclass(frozen=True)
class FeatureBuildOptions:
    feature_id_getter: Callable[[Dict[str, Any]], Any] = lambda p: p.get("Id")
    include_bbox: bool = True
    property_filter: Optional[Callable[[str, Any], bool]] = None


def odata_products_to_feature_collection_geojson(
    odata: Mapping[str, Any],
    opts: FeatureBuildOptions = FeatureBuildOptions(),
) -> geojson.FeatureCollection:
    """
    Convert an OData Products response into a geojson.FeatureCollection.

    Each `odata["value"][i]` becomes a geojson.Feature with:
      - geometry: product["GeoFootprint"]
      - id: opts.feature_id_getter(product)
      - properties: curated OData fields
      - bbox: optional per Feature bbox (and optional top-level bbox)
    """
    products: List[Dict[str, Any]] = list(odata.get("value") or [])
    features: List[geojson.Feature] = []

    # Optional top-level bbox
    minx = miny = float("inf")
    maxx = maxy = float("-inf")
    saw_bbox = False

    for p in products:
        geom_dict = p.get("GeoFootprint")
        if not geom_dict:
            continue

        bbox = _bbox_from_geojson_geometry(geom_dict) if opts.include_bbox else None
        if bbox:
            minx = min(minx, bbox[0])
            miny = min(miny, bbox[1])
            maxx = max(maxx, bbox[2])
            maxy = max(maxy, bbox[3])
            saw_bbox = True

        content_date = p.get("ContentDate") or {}
        props = {
            "id": p.get("Id"),
            "name": p.get("Name"),
            "content_start": _parse_rfc3339(content_date.get("Start")),
            "content_end": _parse_rfc3339(content_date.get("End")),
            "origin_date": _parse_rfc3339(p.get("OriginDate")),
            "publication_date": _parse_rfc3339(p.get("PublicationDate")),
            "modification_date": _parse_rfc3339(p.get("ModificationDate")),
            "online": p.get("Online"),
            "s3_path": p.get("S3Path"),
            "content_type": p.get("ContentType") or p.get("@odata.mediaContentType"),
            "content_length": p.get("ContentLength"),
            "checksum": p.get("Checksum"),
        }
        props = {k: v for k, v in props.items() if v is not None}

        if opts.property_filter is not None:
            props = {k: v for k, v in props.items() if opts.property_filter(k, v)}

        geom = _to_geojson_instance(geom_dict)

        f = geojson.Feature(
            id=opts.feature_id_getter(p),
            geometry=geom,
            properties=props,
        )
        if opts.include_bbox and bbox is not None:
            # GeoJSON objects MAY have a bbox member. :contentReference[oaicite:3]{index=3}
            f["bbox"] = bbox

        features.append(f)

    fc = geojson.FeatureCollection(features)

    next_link = odata.get("@odata.nextLink")
    if next_link:
        # non-standard but often handy
        fc["next"] = next_link

    if opts.include_bbox and saw_bbox:
        fc["bbox"] = [minx, miny, maxx, maxy]

    return fc


def to_feature_collection_geojson(
    odata: Mapping[str, Any],
    output_stream: TextIO,
    opts: FeatureBuildOptions = FeatureBuildOptions(),
):
    feature_collection = odata_products_to_feature_collection_geojson(odata, opts)
    output_stream.write(geojson.dumps(feature_collection, indent=2))
