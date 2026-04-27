"""Nominatim client for place-to-bbox lookup."""

from __future__ import annotations

from typing import Any

import requests

from .bbox import BoundingBox
from .exceptions import DownloadError, InputError

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode_place(place: str, timeout: int = 20, session: requests.Session | None = None) -> BoundingBox:
    """Resolve a place name to a bounding box with Nominatim.

    Parameters
    ----------
    place:
        Human-readable place name, such as `"Berlin"`.
    timeout:
        Request timeout in seconds.
    session:
        Optional preconfigured `requests.Session`.

    Returns
    -------
    BoundingBox
        Bounding box of the first geocoding result.

    Examples
    --------
    >>> isinstance(geocode_place("Lisbon", session=requests.Session()), BoundingBox)
    True
    """

    if not place.strip():
        raise InputError("place name cannot be empty")

    active_session = session or requests.Session()
    headers = {"User-Agent": "osm-area-downloader/0.1 (beginner-cli)"}
    params = {"q": place, "format": "jsonv2", "limit": 1}

    try:
        response = active_session.get(NOMINATIM_URL, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise DownloadError(f"failed to geocode place '{place}': {exc}") from exc

    payload: list[dict[str, Any]] = response.json()
    if not payload:
        raise InputError(f"no location found for '{place}'")

    raw_bbox = payload[0].get("boundingbox")
    if not isinstance(raw_bbox, list) or len(raw_bbox) != 4:
        raise DownloadError("Nominatim response missing boundingbox")

    south, north, west, east = (float(part) for part in raw_bbox)
    return BoundingBox(min_lon=west, min_lat=south, max_lon=east, max_lat=north)

