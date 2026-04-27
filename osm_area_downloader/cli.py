"""Command-line interface for osm-area-downloader."""

from __future__ import annotations

from pathlib import Path

import click

from .exceptions import DownloadError, InputError
from .workflow import run_download


def _infer_format(output: Path, selected: str | None) -> str:
    if selected:
        return selected
    suffix = output.suffix.lower()
    if suffix in {".gpkg"}:
        return "gpkg"
    return "geojson"


@click.command()
@click.option("--place", type=str, help="Place name (example: 'Nairobi')")
@click.option("--bbox", type=str, help="BBox: minlon,minlat,maxlon,maxlat")
@click.option("--output", required=True, type=click.Path(path_type=Path), help="Output file path")
@click.option("--format", "output_format", type=click.Choice(["geojson", "gpkg"]), default=None)
def main(place: str | None, bbox: str | None, output: Path, output_format: str | None) -> None:
    """Download OSM features for a place or bbox and save them locally.

    Parameters
    ----------
    place:
        Optional place name to geocode via Nominatim.
    bbox:
        Optional `minlon,minlat,maxlon,maxlat` bbox string.
    output:
        Path to resulting file.
    output_format:
        Optional explicit output format.

    Examples
    --------
    >>> # python -m osm_area_downloader --bbox "-0.5,51.2,0.3,51.8" --output london.geojson
    >>> # python -m osm_area_downloader --place "Lisbon" --output lisbon.gpkg --format gpkg
    """

    chosen_format = _infer_format(output, output_format)

    try:
        feature_collection = run_download(
            place=place,
            bbox=bbox,
            output_path=output,
            output_format=chosen_format,
        )
    except (InputError, DownloadError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Downloaded {len(feature_collection['features'])} features")
    click.echo(f"Saved {chosen_format.upper()} to {output}")


if __name__ == "__main__":  # pragma: no cover
    main()
