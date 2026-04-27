from pathlib import Path

import pytest


def test_write_geopackage_with_real_geopandas(tmp_path: Path) -> None:
    geopandas = pytest.importorskip("geopandas")

    from osm_area_downloader.writers import write_geopackage

    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [13.405, 52.52]},
                "properties": {"name": "Berlin"},
            }
        ],
    }

    output = tmp_path / "integration.gpkg"
    write_geopackage(feature_collection, output)

    loaded = geopandas.read_file(output, layer="osm_features")
    assert output.exists()
    assert len(loaded) == 1
    assert loaded.iloc[0]["name"] == "Berlin"

