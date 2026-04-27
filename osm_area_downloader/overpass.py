"""Overpass query and conversion helpers."""

from __future__ import annotations

from typing import Any

import requests

from .bbox import BoundingBox
from .exceptions import DownloadError

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def build_query(bbox: BoundingBox) -> str:
    """Build an Overpass QL query for nodes, ways, and relations.

    Parameters
    ----------
    bbox:
        Bounding box used to filter OSM features.

    Returns
    -------
    str
        Overpass query string.

    Examples
    --------
    >>> "node" in build_query(BoundingBox(1, 2, 3, 4))
    True
    """

    south, west, north, east = bbox.to_overpass_tuple()
    area = f"({south},{west},{north},{east})"
    return (
        "[out:json][timeout:30];"
        "("  # Collect common OSM geometry types.
        f"node{area};"
        f"way{area};"
        f"relation{area};"
        ");"
        "out body geom;"
    )


def fetch_geojson_features(
    bbox: BoundingBox,
    timeout: int = 60,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Download OSM data from Overpass and convert it to GeoJSON.

    Parameters
    ----------
    bbox:
        Bounding box used for querying.
    timeout:
        Request timeout in seconds.
    session:
        Optional preconfigured `requests.Session`.

    Returns
    -------
    dict[str, Any]
        GeoJSON FeatureCollection.

    Examples
    --------
    >>> fc = {"type": "FeatureCollection", "features": []}
    >>> isinstance(fc["features"], list)
    True
    """

    active_session = session or requests.Session()
    query = build_query(bbox)

    try:
        response = active_session.post(OVERPASS_URL, data={"data": query}, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise DownloadError(f"failed to query Overpass API: {exc}") from exc

    payload = response.json()
    return osm_json_to_geojson(payload)


def osm_json_to_geojson(payload: dict[str, Any]) -> dict[str, Any]:
    """Convert Overpass JSON payload into a compact FeatureCollection.

    Parameters
    ----------
    payload:
        JSON dictionary returned by Overpass API.

    Returns
    -------
    dict[str, Any]
        GeoJSON FeatureCollection with OSM tags in properties.

    Examples
    --------
    >>> osm_json_to_geojson({"elements": []})
    {'type': 'FeatureCollection', 'features': []}
    """

    features: list[dict[str, Any]] = []
    for element in payload.get("elements", []):
        feature = _element_to_feature(element)
        if feature is not None:
            features.append(feature)

    return {"type": "FeatureCollection", "features": features}


def _element_to_feature(element: dict[str, Any]) -> dict[str, Any] | None:
    geometry = _element_geometry(element)
    if geometry is None:
        return None

    tags = element.get("tags", {})
    return {
        "type": "Feature",
        "geometry": geometry,
        "properties": {
            "osm_id": element.get("id"),
            "osm_type": element.get("type"),
            **tags,
        },
    }


def _element_geometry(element: dict[str, Any]) -> dict[str, Any] | None:
    osm_type = element.get("type")
    if osm_type == "node" and "lat" in element and "lon" in element:
        return {"type": "Point", "coordinates": [element["lon"], element["lat"]]}

    geometry_points = element.get("geometry")
    if not isinstance(geometry_points, list) or len(geometry_points) < 2:
        return None

    coordinates = [[point["lon"], point["lat"]] for point in geometry_points]
    is_polygon = len(coordinates) >= 4 and coordinates[0] == coordinates[-1]

    if is_polygon:
        return {"type": "Polygon", "coordinates": [coordinates]}
    return {"type": "LineString", "coordinates": coordinates}

