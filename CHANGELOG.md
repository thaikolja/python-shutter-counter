# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1.2.0

**Released:** 2026-04-02

### Added

- CLI with flexible argument parsing (`-i`/`--input`, `-c`/`--clean`, `-v`/`--verbose`)
- Thousand separators in shutter count output (e.g., `83,002`)
- `ShutterCountResult` dataclass with `camera_make`, `camera_model`, and `shutter_count`
- Comprehensive docstrings across all modules
- Dedicated CLI tests in `tests/test_cli.py`

### Changed

- Refactored package structure: `counter.py` (core logic), `cli.py` (CLI entry point)
- Image path is now optional; accepts positional argument or `--input` flag
- `get_shutter_count()` now returns a `ShutterCountResult` instead of a raw value
- Cleaned up camera make/model strings (strips `" CORPORATION"` and `"NIKON "` prefix)
- Updated GitLab CI/CD with proper lint, test, and build stages using Docker images

### Fixed

- MakerNote tags now parsed correctly (`details=True` in `exifread.process_file`)
- Removed duplicate `main.py` and unused imports

## v1.1.0

**Released:** 2024-07-29

### Added

- GitHub Actions CI/CD workflow
- `CHANGELOG.md` file

### Changed

- Updated GitLab CI/CD pipeline configuration

## v1.0.0
**Released:** 2024-07-27

### Added

- Initial implementation of Shutter Counter for Nikon D850, D810, and D800
- EXIF data parsing with `exifread`
- Support for `int` and `str` output types
- `LICENSE` (MIT)
- Documentation and usage instructions

### Fixed

- Output when the `str` parameter is provided

## v0.0.1

**Released:** 2024-04-06

### Added

- First commit of the Shutter Counter script
- Basic shutter count extraction from Nikon DSLR images
