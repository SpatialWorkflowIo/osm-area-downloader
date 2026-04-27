"""High-level workflow orchestration helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .bbox import BoundingBox, parse_bbox
from .exceptions import InputError
from .nominatim import geocode_place
from .overpass import fetch_geojson_features
from .writers import write_geojson, write_geopackage


def resolve_bbox(place: str | None, bbox: str | None) -> BoundingBox:
    """Resolve CLI input into a validated bounding box.

    Parameters
    ----------
    place:
        Place-name input from CLI, if provided.
    bbox:
        BBox text input from CLI, if provided.

    Returns
    -------
    BoundingBox
        Final bounding box used for Overpass queries.

    Examples
    --------
    >>> resolve_bbox(None, "-0.5,51.2,0.3,51.8")
    BoundingBox(min_lon=-0.5, min_lat=51.2, max_lon=0.3, max_lat=51.8)
    """

    if bool(place) == bool(bbox):
        raise InputError("provide exactly one of --place or --bbox")
    if place:
        return geocode_place(place)
    assert bbox is not None
    return parse_bbox(bbox)


def run_download(place: str | None, bbox: str | None, output_path: Path, output_format: str) -> dict[str, Any]:
    """Execute full download pipeline and write output file.

    Parameters
    ----------
    place:
        Place name for geocoding mode.
    bbox:
        Bounding box text for direct mode.
    output_path:
        Destination path for output file.
    output_format:
        Either `"geojson"` or `"gpkg"`.

    Returns
    -------
    dict[str, Any]
        GeoJSON FeatureCollection returned from the API conversion step.

    Examples
    --------
    >>> run_download(None, "-0.5,51.2,0.3,51.8", Path("out.geojson"), "geojson")
    {'type': 'FeatureCollection', 'features': []}
    """

    resolved_bbox = resolve_bbox(place=place, bbox=bbox)
    feature_collection = fetch_geojson_features(resolved_bbox)

    if output_format == "geojson":
        write_geojson(feature_collection, output_path)
    elif output_format == "gpkg":
        write_geopackage(feature_collection, output_path)
    else:
        raise InputError("output format must be 'geojson' or 'gpkg'")

    return feature_collection

