import requests

from osm_area_downloader.bbox import BoundingBox
from osm_area_downloader.exceptions import DownloadError, InputError
from osm_area_downloader.nominatim import geocode_place


class DummyResponse:
    def __init__(self, payload, should_raise: bool = False):
        self._payload = payload
        self._should_raise = should_raise

    def raise_for_status(self) -> None:
        if self._should_raise:
            raise requests.HTTPError("boom")

    def json(self):
        return self._payload


class DummySession:
    def __init__(self, response=None, exc: Exception | None = None):
        self.response = response
        self.exc = exc

    def get(self, *args, **kwargs):
        if self.exc:
            raise self.exc
        return self.response


def test_geocode_place_success() -> None:
    payload = [{"boundingbox": ["51.2", "51.8", "-0.5", "0.3"]}]
    bbox = geocode_place("London", session=DummySession(response=DummyResponse(payload)))
    assert bbox == BoundingBox(min_lon=-0.5, min_lat=51.2, max_lon=0.3, max_lat=51.8)


def test_geocode_place_rejects_empty_name() -> None:
    try:
        geocode_place("  ")
    except InputError as exc:
        assert "empty" in str(exc)
    else:
        raise AssertionError("Expected InputError")


def test_geocode_place_handles_request_errors() -> None:
    try:
        geocode_place("London", session=DummySession(exc=requests.RequestException("offline")))
    except DownloadError as exc:
        assert "failed to geocode" in str(exc)
    else:
        raise AssertionError("Expected DownloadError")


def test_geocode_place_handles_no_results() -> None:
    try:
        geocode_place("Nowhere", session=DummySession(response=DummyResponse([])))
    except InputError as exc:
        assert "no location" in str(exc)
    else:
        raise AssertionError("Expected InputError")


def test_geocode_place_handles_missing_bbox() -> None:
    try:
        geocode_place("Nowhere", session=DummySession(response=DummyResponse([{}])))
    except DownloadError as exc:
        assert "boundingbox" in str(exc)
    else:
        raise AssertionError("Expected DownloadError")

