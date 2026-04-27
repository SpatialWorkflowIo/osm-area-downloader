from pathlib import Path

from click.testing import CliRunner

from osm_area_downloader.cli import _infer_format, main


def test_infer_format_uses_suffix_and_explicit_option() -> None:
    assert _infer_format(Path("x.gpkg"), None) == "gpkg"
    assert _infer_format(Path("x.any"), None) == "geojson"
    assert _infer_format(Path("x.any"), "gpkg") == "gpkg"


def test_cli_success(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "osm_area_downloader.cli.run_download",
        lambda **kwargs: {"type": "FeatureCollection", "features": [{}, {}]},
    )
    runner = CliRunner()
    result = runner.invoke(main, ["--bbox", "1,2,3,4", "--output", str(tmp_path / "out.geojson")])
    assert result.exit_code == 0
    assert "Downloaded 2 features" in result.output


def test_cli_handles_errors(monkeypatch, tmp_path: Path) -> None:
    from osm_area_downloader.exceptions import InputError

    def fail(**kwargs):
        raise InputError("bad input")

    monkeypatch.setattr("osm_area_downloader.cli.run_download", fail)

    runner = CliRunner()
    result = runner.invoke(main, ["--bbox", "1,2,3,4", "--output", str(tmp_path / "out.geojson")])
    assert result.exit_code != 0
    assert "bad input" in result.output


def test_main_module_importable() -> None:
    import osm_area_downloader.__main__ as entry

    assert entry.main is not None
