import requests

from osm_area_downloader.bbox import BoundingBox
from osm_area_downloader.exceptions import DownloadError, InputError
from osm_area_downloader.overpass import build_query, fetch_geojson_features, osm_json_to_geojson


class DummyResponse:
    def __init__(self, payload, should_raise: bool = False, status_code: int = 200, text: str = ""):
        self._payload = payload
        self._should_raise = should_raise
        self.status_code = status_code
        self.text = text

    def raise_for_status(self) -> None:
        if self._should_raise:
            raise requests.HTTPError("bad status", response=self)

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


class CaptureSession:
    def __init__(self, response):
        self.response = response
        self.last_headers = None

    def post(self, *args, **kwargs):
        self.last_headers = kwargs.get("headers")
        return self.response


class SequenceSession:
    def __init__(self, responses):
        self.responses = responses
        self.calls = 0

    def post(self, *args, **kwargs):
        response = self.responses[self.calls]
        self.calls += 1
        return response


def test_build_query_includes_bbox() -> None:
    text = build_query(BoundingBox(-0.5, 51.2, 0.3, 51.8), preset="all")
    assert "node" in text
    assert "(51.2,-0.5,51.8,0.3)" in text


def test_build_query_presets() -> None:
    bbox = BoundingBox(-0.5, 51.2, 0.3, 51.8)
    roads = build_query(bbox, preset="roads")
    buildings = build_query(bbox, preset="buildings")
    pois = build_query(bbox, preset="pois")

    assert "way[highway]" in roads
    assert "relation[type=route][route=road]" in roads
    assert "way[building]" in buildings
    assert "relation[building]" in buildings
    assert "node[amenity]" in pois
    assert "node[tourism]" in pois
    assert "node[shop]" in pois


def test_build_query_rejects_unknown_preset() -> None:
    try:
        build_query(BoundingBox(-0.5, 51.2, 0.3, 51.8), preset="water")
    except InputError as exc:
        assert "preset" in str(exc)
    else:
        raise AssertionError("Expected InputError")


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
    result = fetch_geojson_features(BoundingBox(-1, -1, 1, 1), preset="roads", session=session)
    assert len(result["features"]) == 1


def test_fetch_geojson_features_sets_headers() -> None:
    payload = {"elements": [{"type": "node", "id": 1, "lat": 1, "lon": 2}]}
    session = CaptureSession(response=DummyResponse(payload))
    fetch_geojson_features(BoundingBox(-1, -1, 1, 1), preset="roads", session=session)
    assert session.last_headers is not None
    assert "User-Agent" in session.last_headers


def test_fetch_geojson_features_handles_request_errors() -> None:
    session = DummySession(exc=requests.RequestException("offline"))
    try:
        fetch_geojson_features(BoundingBox(-1, -1, 1, 1), session=session)
    except DownloadError as exc:
        assert "Overpass" in str(exc)
    else:
        raise AssertionError("Expected DownloadError")


def test_fetch_geojson_features_handles_http_errors_with_hint() -> None:
    session = DummySession(
        response=DummyResponse(
            {"elements": []},
            should_raise=True,
            status_code=504,
            text="busy",
        )
    )
    try:
        fetch_geojson_features(BoundingBox(-1, -1, 1, 1), session=session)
    except DownloadError as exc:
        assert "HTTP 504" in str(exc)
        assert "smaller bbox" in str(exc)
    else:
        raise AssertionError("Expected DownloadError")


def test_fetch_geojson_features_retries_on_busy_endpoint() -> None:
    busy = DummyResponse({"elements": []}, should_raise=True, status_code=504, text="busy")
    ok = DummyResponse({"elements": [{"type": "node", "id": 1, "lat": 1, "lon": 2}]})
    session = SequenceSession([busy, ok])
    result = fetch_geojson_features(BoundingBox(-1, -1, 1, 1), session=session)
    assert session.calls == 2
    assert len(result["features"]) == 1


def test_fetch_geojson_features_reports_406_with_hint() -> None:
    session = DummySession(
        response=DummyResponse(
            {"elements": []},
            should_raise=True,
            status_code=406,
            text="not acceptable",
        )
    )
    try:
        fetch_geojson_features(BoundingBox(-1, -1, 1, 1), session=session)
    except DownloadError as exc:
        assert "HTTP 406" in str(exc)
        assert "rejected" in str(exc)
    else:
        raise AssertionError("Expected DownloadError")


