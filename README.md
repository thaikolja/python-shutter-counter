# Shutter Counter

[![Pipeline Status](https://gitlab.com/thaikolja/python-shutter-counter/badges/main/pipeline.svg)](https://gitlab.com/thaikolja/python-shutter-counter/commits/main) [![Coverage Status](https://gitlab.com/thaikolja/python-shutter-counter/badges/main/coverage.svg)](https://gitlab.com/thaikolja/python-shutter-counter/commits/main) [![PyPI version](https://badge.fury.io/py/shutter-counter.svg)](https://badge.fury.io/py/shutter-counter) [![Python Version](https://img.shields.io/pypi/pyversions/shutter-counter.svg)](https://pypi.org/project/shutter-counter/)

Extract the shutter actuation count from Nikon camera images using EXIF metadata.

## Features

- Supports most Nikon DSLR models (D1–D6 series, D8xx, D7xx, D5xx, D3xxx, and Z-series)
- Reads shutter count from MakerNote EXIF tags
- Clean numeric output for scripting
- Thousand separators in human-readable output
- Works with JPEG and NEF files

## Installation

### As Global Binary

```bash
pipx install shutter-counter
```

### From Git Source

```bash
# pip
pip install -e .
```

### Development

```bash
pip install -e ".[dev]"
```

## Usage

### Command Line

```bash
# Basic usage (positional argument)
python main.py image.jpg

# Using explicit flag
python main.py --input image.jpg

# Clean output (number only, with thousand separators)
python main.py image.jpg --clean

# Verbose mode
python main.py image.jpg -v

# Help
python main.py --help
```

### Example Output

```bash
$ python main.py image.jpg
Shutter count for NIKON D850 is 82,222

$ python main.py image.jpg --clean
82,222
```

### Python API

```python
from shutter_counter.counter import ShutterCounter

counter = ShutterCounter("image.jpg")
result = counter.get_shutter_count()

print(f"Camera: {result.camera_make} {result.camera_model}")
print(f"Shutter count: {result.shutter_count:,}")
```

## Supported Cameras

### Newer Models

- NIKON D6, D850, D780, D500, D7500
- NIKON Z7, Z6, Z5, Z6II, Z7II

### Older Models

- NIKON D810, D800, Df, D610, D750
- NIKON D700, D300S, D300, D200, D100
- NIKON D90, D70s, D70, D60, D50, D40x, D40
- NIKON D1X, D1H, D1, D2Xs, D2X, D2Hs, D2H
- NIKON D3X, D3S, D3, D4S, D4, D5, D3500

## Requirements

- Python 3.10+
- `exifread >= 3.0.0`

## Testing

```bash
pytest tests/ -v
```

## License

MIT License - see LICENSE file for details.
