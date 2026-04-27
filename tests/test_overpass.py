import requests

from osm_area_downloader.bbox import BoundingBox
from osm_area_downloader.exceptions import DownloadError
from osm_area_downloader.overpass import build_query, fetch_geojson_features, osm_json_to_geojson


class DummyResponse:
    def __init__(self, payload, should_raise: bool = False):
        self._payload = payload
        self._should_raise = should_raise

    def raise_for_status(self) -> None:
        if self._should_raise:
            raise requests.HTTPError("bad status")

    def json(self):
        return self._payload


class DummySession:
    def __init__(self, response=None, exc: Exception | None = None):
        self.response = response
        self.exc = exc

    def post(self, *args, **kwargs):
        if self.exc:
            raise self.exc
        return self.response


def test_build_query_includes_bbox() -> None:
    text = build_query(BoundingBox(-0.5, 51.2, 0.3, 51.8))
    assert "node" in text
    assert "(51.2,-0.5,51.8,0.3)" in text


def test_osm_json_to_geojson_converts_node_way_and_polygon() -> None:
    payload = {
        "elements": [
            {"type": "node", "id": 1, "lat": 10.0, "lon": 20.0, "tags": {"name": "A"}},
            {
                "type": "way",
                "id": 2,
                "geometry": [{"lat": 0, "lon": 0}, {"lat": 1, "lon": 1}],
                "tags": {"highway": "path"},
            },
            {
                "type": "way",
                "id": 3,
                "geometry": [
                    {"lat": 0, "lon": 0},
                    {"lat": 0, "lon": 1},
                    {"lat": 1, "lon": 1},
                    {"lat": 0, "lon": 0},
                ],
            },
            {"type": "relation", "id": 4},
        ]
    }
    feature_collection = osm_json_to_geojson(payload)
    assert feature_collection["type"] == "FeatureCollection"
    assert len(feature_collection["features"]) == 3
    assert feature_collection["features"][0]["geometry"]["type"] == "Point"
    assert feature_collection["features"][1]["geometry"]["type"] == "LineString"
    assert feature_collection["features"][2]["geometry"]["type"] == "Polygon"


def test_fetch_geojson_features_success() -> None:
    payload = {"elements": [{"type": "node", "id": 1, "lat": 1, "lon": 2}]}
    session = DummySession(response=DummyResponse(payload))
    result = fetch_geojson_features(BoundingBox(-1, -1, 1, 1), session=session)
    assert len(result["features"]) == 1


def test_fetch_geojson_features_handles_request_errors() -> None:
    session = DummySession(exc=requests.RequestException("offline"))
    try:
        fetch_geojson_features(BoundingBox(-1, -1, 1, 1), session=session)
    except DownloadError as exc:
        assert "Overpass" in str(exc)
    else:
        raise AssertionError("Expected DownloadError")

