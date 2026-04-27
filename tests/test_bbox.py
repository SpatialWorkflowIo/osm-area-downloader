from osm_area_downloader.bbox import BoundingBox, parse_bbox
from osm_area_downloader.exceptions import InputError


def test_parse_bbox_success() -> None:
    bbox = parse_bbox("-0.5,51.2,0.3,51.8")
    assert bbox == BoundingBox(min_lon=-0.5, min_lat=51.2, max_lon=0.3, max_lat=51.8)
    assert bbox.to_overpass_tuple() == (51.2, -0.5, 51.8, 0.3)


def test_parse_bbox_requires_four_values() -> None:
    try:
        parse_bbox("1,2,3")
    except InputError as exc:
        assert "four" in str(exc)
    else:
        raise AssertionError("Expected InputError")


def test_parse_bbox_rejects_non_numeric_values() -> None:
    try:
        parse_bbox("a,2,3,4")
    except InputError as exc:
        assert "numeric" in str(exc)
    else:
        raise AssertionError("Expected InputError")


def test_bbox_order_validation() -> None:
    try:
        BoundingBox(1, 1, 0, 2)
    except InputError as exc:
        assert "minlon" in str(exc)
    else:
        raise AssertionError("Expected InputError")

    try:
        BoundingBox(0, 2, 1, 1)
    except InputError as exc:
        assert "minlat" in str(exc)
    else:
        raise AssertionError("Expected InputError")

