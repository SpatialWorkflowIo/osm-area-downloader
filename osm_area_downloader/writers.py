"""Output writers for GeoJSON and GeoPackage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .exceptions import DownloadError


def write_geojson(feature_collection: dict[str, Any], output_path: Path) -> None:
    """Write a GeoJSON FeatureCollection to disk.

    Parameters
    ----------
    feature_collection:
        GeoJSON payload dictionary.
    output_path:
        Destination file path.

    Examples
    --------
    >>> from pathlib import Path
    >>> write_geojson({"type": "FeatureCollection", "features": []}, Path("out.geojson"))
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(feature_collection, indent=2), encoding="utf-8")


def write_geopackage(feature_collection: dict[str, Any], output_path: Path, layer: str = "osm_features") -> None:
    """Write a FeatureCollection to GeoPackage using GeoPandas.

    Parameters
    ----------
    feature_collection:
        GeoJSON payload dictionary.
    output_path:
        Destination `.gpkg` file.
    layer:
        Output layer name inside the GeoPackage.

    Examples
    --------
    >>> # Requires optional dependency: geopandas
    >>> isinstance(layer, str)
    True
    """

    try:
        import geopandas as gpd
    except Exception as exc:  # pragma: no cover - import branch tested via monkeypatch
        raise DownloadError(
            "GeoPackage export requires geopandas. Install with: pip install geopandas"
        ) from exc

    geo_df = gpd.GeoDataFrame.from_features(feature_collection.get("features", []), crs="EPSG:4326")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        geo_df.to_file(output_path, layer=layer, driver="GPKG")
    except Exception as exc:
        raise DownloadError(f"failed to write GeoPackage: {exc}") from exc
