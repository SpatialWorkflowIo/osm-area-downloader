import json
from pathlib import Path

from osm_area_downloader.exceptions import DownloadError, InputError
from osm_area_downloader.workflow import resolve_bbox, run_download
from osm_area_downloader.writers import write_geojson, write_geopackage


def test_resolve_bbox_validation() -> None:
    for place, bbox in [(None, None), ("A", "1,2,3,4")]:
        try:
            resolve_bbox(place, bbox)
        except InputError as exc:
            assert "exactly one" in str(exc)
        else:
            raise AssertionError("Expected InputError")


def test_resolve_bbox_from_bbox_string() -> None:
    bbox = resolve_bbox(None, "-0.5,51.2,0.3,51.8")
    assert bbox.min_lon == -0.5


def test_resolve_bbox_from_place(monkeypatch) -> None:
    from osm_area_downloader.bbox import BoundingBox

    monkeypatch.setattr("osm_area_downloader.workflow.geocode_place", lambda place: BoundingBox(1, 2, 3, 4))
    assert resolve_bbox("Lisbon", None).max_lat == 4


def test_run_download_geojson(monkeypatch, tmp_path: Path) -> None:
    from osm_area_downloader.bbox import BoundingBox

    monkeypatch.setattr("osm_area_downloader.workflow.resolve_bbox", lambda place, bbox: BoundingBox(1, 2, 3, 4))
    monkeypatch.setattr(
        "osm_area_downloader.workflow.fetch_geojson_features",
        lambda bbox: {"type": "FeatureCollection", "features": []},
    )

    output = tmp_path / "out.geojson"
    result = run_download(None, "1,2,3,4", output, "geojson")
    assert result["type"] == "FeatureCollection"
    assert output.exists()


def test_run_download_gpkg_calls_writer(monkeypatch, tmp_path: Path) -> None:
    from osm_area_downloader.bbox import BoundingBox

    called = {"writer": False}
    monkeypatch.setattr("osm_area_downloader.workflow.resolve_bbox", lambda place, bbox: BoundingBox(1, 2, 3, 4))
    monkeypatch.setattr(
        "osm_area_downloader.workflow.fetch_geojson_features",
        lambda bbox: {"type": "FeatureCollection", "features": []},
    )

    def fake_write_geopackage(feature_collection, output_path):
        called["writer"] = True

    monkeypatch.setattr("osm_area_downloader.workflow.write_geopackage", fake_write_geopackage)
    run_download(None, "1,2,3,4", tmp_path / "out.gpkg", "gpkg")
    assert called["writer"] is True


def test_run_download_rejects_unknown_format(monkeypatch, tmp_path: Path) -> None:
    from osm_area_downloader.bbox import BoundingBox

    monkeypatch.setattr("osm_area_downloader.workflow.resolve_bbox", lambda place, bbox: BoundingBox(1, 2, 3, 4))
    monkeypatch.setattr(
        "osm_area_downloader.workflow.fetch_geojson_features",
        lambda bbox: {"type": "FeatureCollection", "features": []},
    )

    try:
        run_download(None, "1,2,3,4", tmp_path / "out.bin", "bin")
    except InputError as exc:
        assert "geojson" in str(exc)
    else:
        raise AssertionError("Expected InputError")


def test_write_geojson(tmp_path: Path) -> None:
    output = tmp_path / "result.geojson"
    write_geojson({"type": "FeatureCollection", "features": []}, output)
    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["type"] == "FeatureCollection"


def test_write_geopackage_without_geopandas(monkeypatch, tmp_path: Path) -> None:
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "geopandas":
            raise ImportError("missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    try:
        write_geopackage({"type": "FeatureCollection", "features": []}, tmp_path / "x.gpkg")
    except DownloadError as exc:
        assert "geopandas" in str(exc)
    else:
        raise AssertionError("Expected DownloadError")


def test_write_geopackage_success_with_fake_geopandas(monkeypatch, tmp_path: Path) -> None:
    class FakeGeoDataFrame:
        def __init__(self):
            self.called = False

        def to_file(self, output_path, layer, driver):
            self.called = True
            assert output_path == tmp_path / "ok.gpkg"
            assert layer == "osm_features"
            assert driver == "GPKG"

    class FakeGeoPandasModule:
        class GeoDataFrame:
            @staticmethod
            def from_features(features, crs):
                assert crs == "EPSG:4326"
                return FakeGeoDataFrame()

    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "geopandas":
            return FakeGeoPandasModule()
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    write_geopackage({"type": "FeatureCollection", "features": []}, tmp_path / "ok.gpkg")


def test_write_geopackage_write_failure(monkeypatch, tmp_path: Path) -> None:
    class FakeGeoDataFrame:
        def to_file(self, output_path, layer, driver):
            raise RuntimeError("write failed")

    class FakeGeoPandasModule:
        class GeoDataFrame:
            @staticmethod
            def from_features(features, crs):
                return FakeGeoDataFrame()

    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "geopandas":
            return FakeGeoPandasModule()
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    try:
        write_geopackage({"type": "FeatureCollection", "features": []}, tmp_path / "bad.gpkg")
    except DownloadError as exc:
        assert "failed to write" in str(exc)
    else:
        raise AssertionError("Expected DownloadError")

