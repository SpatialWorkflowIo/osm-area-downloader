"""Bounding box parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .exceptions import InputError


@dataclass(frozen=True)
class BoundingBox:
    """Geographic bounding box in lon/lat order.

    Parameters
    ----------
    min_lon:
        Western longitude.
    min_lat:
        Southern latitude.
    max_lon:
        Eastern longitude.
    max_lat:
        Northern latitude.

    Examples
    --------
    >>> BoundingBox(-0.5, 51.2, 0.3, 51.8).to_overpass_tuple()
    (51.2, -0.5, 51.8, 0.3)
    """

    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

    def __post_init__(self) -> None:
        if self.min_lon >= self.max_lon:
            raise InputError("minlon must be smaller than maxlon")
        if self.min_lat >= self.max_lat:
            raise InputError("minlat must be smaller than maxlat")

    def to_overpass_tuple(self) -> tuple[float, float, float, float]:
        """Return tuple order required by Overpass API.

        Returns
        -------
        tuple[float, float, float, float]
            `(south, west, north, east)` values.

        Examples
        --------
        >>> BoundingBox(1, 2, 3, 4).to_overpass_tuple()
        (2, 1, 4, 3)
        """

        return (self.min_lat, self.min_lon, self.max_lat, self.max_lon)


def parse_bbox(value: str) -> BoundingBox:
    """Parse a CLI bbox string into a validated object.

    Parameters
    ----------
    value:
        Raw string in `minlon,minlat,maxlon,maxlat` format.

    Returns
    -------
    BoundingBox
        Validated bounding box object.

    Examples
    --------
    >>> parse_bbox("-0.5,51.2,0.3,51.8")
    BoundingBox(min_lon=-0.5, min_lat=51.2, max_lon=0.3, max_lat=51.8)
    """

    parts = [piece.strip() for piece in value.split(",")]
    if len(parts) != 4:
        raise InputError("bbox must have four comma-separated numbers")

    try:
        min_lon, min_lat, max_lon, max_lat = (float(part) for part in parts)
    except ValueError as exc:
        raise InputError("bbox values must be numeric") from exc

    return BoundingBox(min_lon=min_lon, min_lat=min_lat, max_lon=max_lon, max_lat=max_lat)

