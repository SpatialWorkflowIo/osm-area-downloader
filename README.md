# OSM Area Downloader (GeoJSON + GeoPackage)

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](#quickstart)
[![CI](https://github.com/SpatialWorkflowIo/osm-area-downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/SpatialWorkflowIo/osm-area-downloader/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](#testing)

`osm-area-downloader` is a beginner-friendly command-line tool for downloading OpenStreetMap (OSM) features for a place name or bounding box, then exporting clean **GeoJSON** or **GeoPackage** files.

If you are new to GIS automation, this project gives you a simple one-line workflow and practical examples. Learn more about spatial automation at [Spatial Workflow](https://spatialworkflow.io/).

## Quickstart

```bash
source .venv/bin/activate
pip install -r requirements.txt
python -m osm_area_downloader --bbox "-0.150,51.500,-0.120,51.520" --preset roads --output london-roads.geojson
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
  --bbox "-0.150,51.500,-0.120,51.520" \
  --preset roads \
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

### Example 4: Download roads only

```bash
python -m osm_area_downloader \
  --place "Berlin" \
  --preset roads \
  --output berlin-roads.geojson
```

## Input rules

- Use exactly one of `--place` or `--bbox`.
- `--bbox` must be in this order: `minlon,minlat,maxlon,maxlat`.
- If `--format` is omitted, format is inferred from output extension (`.gpkg` => GeoPackage; otherwise GeoJSON).
- `--preset` controls feature filtering: `all`, `roads`, `buildings`, `pois`.

## Output

- **GeoJSON**: always available.
- **GeoPackage**: requires `geopandas`.

If GeoPackage export fails because dependencies are missing, install:

```bash
pip install geopandas
```

If Overpass returns busy/timeout HTTP errors (for example 429 or 504), retry with a smaller bbox or use a focused preset like `--preset roads`.

## Troubleshooting Overpass errors

If the Overpass API is busy, common retry strategies are:

- use a smaller bbox
- use a focused preset instead of `all`
- retry the same command a few minutes later

### Retry with a smaller roads query

```bash
python -m osm_area_downloader \
  --bbox "-0.150,51.500,-0.120,51.520" \
  --preset roads \
  --output london-roads.geojson
```

### Retry with a buildings-only query

```bash
python -m osm_area_downloader \
  --bbox "-0.150,51.500,-0.120,51.520" \
  --preset buildings \
  --output london-buildings.geojson
```

### Retry with POIs only

```bash
python -m osm_area_downloader \
  --bbox "-0.150,51.500,-0.120,51.520" \
  --preset pois \
  --output london-pois.geojson
```

### Retry by place name instead of bbox

```bash
python -m osm_area_downloader \
  --place "Berlin" \
  --preset roads \
  --output berlin-roads.geojson
```

## Testing

Run a quick local test pass:

```bash
pytest
```

Run tests with the strict 100% coverage gate used in CI:

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

