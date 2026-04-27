# Changelog

All notable changes to `osm-area-downloader` are documented in this file.

## v0.1.0 - 2026-04-27

### Added
- Initial CLI release with `python -m osm_area_downloader` entrypoint.
- Input modes for place geocoding (`--place`) and raw bbox (`--bbox`).
- Overpass download pipeline and OSM-to-GeoJSON conversion.
- Output writers for GeoJSON and optional GeoPackage (`--format gpkg`).
- Query presets with `--preset`: `all`, `roads`, `buildings`, and `pois`.
- Test suite with strict 100% coverage enforcement.
- GitHub Actions CI workflow that runs tests and coverage gate on push/PR.

