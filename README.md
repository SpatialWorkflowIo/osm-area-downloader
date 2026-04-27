# OSM Area Downloader (GeoJSON + GeoPackage)

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](#quickstart)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](#testing)

`osm-area-downloader` is a beginner-friendly command-line tool for downloading OpenStreetMap (OSM) features for a place name or bounding box, then exporting clean **GeoJSON** or **GeoPackage** files.

If you are new to GIS automation, this project gives you a simple one-line workflow and practical examples. Learn more about spatial automation at [Spatial Workflow](https://spatialworkflow.io/).

## Quickstart

```bash
source .venv/bin/activate
pip install -r requirements.txt
python -m osm_area_downloader --bbox "-0.5103,51.2868,0.3340,51.6919" --output london.geojson
```

## Why this tool exists

- Make OSM downloads easy for beginners.
- Accept either a place name or raw bbox coordinates.
- Produce formats that open directly in common GIS software.

## Usage

Show help:

```bash
python -m osm_area_downloader --help
```

### Example 1: Download by bounding box (GeoJSON)

```bash
python -m osm_area_downloader \
  --bbox "-0.5103,51.2868,0.3340,51.6919" \
  --output london.geojson
```

### Example 2: Download by place name (GeoJSON)

```bash
python -m osm_area_downloader \
  --place "Lisbon" \
  --output lisbon.geojson
```

### Example 3: Download by place name (GeoPackage)

```bash
python -m osm_area_downloader \
  --place "Nairobi" \
  --output nairobi.gpkg \
  --format gpkg
```

## Input rules

- Use exactly one of `--place` or `--bbox`.
- `--bbox` must be in this order: `minlon,minlat,maxlon,maxlat`.
- If `--format` is omitted, format is inferred from output extension (`.gpkg` => GeoPackage; otherwise GeoJSON).

## Output

- **GeoJSON**: always available.
- **GeoPackage**: requires `geopandas`.

If GeoPackage export fails because dependencies are missing, install:

```bash
pip install geopandas
```

## Testing

Run tests with strict 100% coverage:

```bash
pytest --cov=osm_area_downloader --cov-report=term-missing --cov-fail-under=100
```

## Development notes

- Entry point: `osm_area_downloader/__main__.py`
- Core modules:
  - `osm_area_downloader/nominatim.py` (place -> bbox)
  - `osm_area_downloader/overpass.py` (bbox -> OSM features)
  - `osm_area_downloader/writers.py` (GeoJSON/GeoPackage output)
  - `osm_area_downloader/workflow.py` (pipeline orchestration)

## Links

- Project support and GIS automation ideas: [https://spatialworkflow.io/](https://spatialworkflow.io/)
- OpenStreetMap Nominatim: https://nominatim.openstreetmap.org/
- Overpass API: https://overpass-api.de/

