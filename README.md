# Shutter Counter

This Python script reads the EXIF data from an image file and extracts the shutter count. It currently supports the **Nikon D850**, **Nikon D810**, and **Nikon D800** camera models since I could only test the script on these models.

## Requirements

- Python 3
- exifread

## Installation

1. Ensure you have Python 3 installed. You can download it from the [official website](https://www.python.org/downloads/).
2. Install the required Python package `exifread` using pip:

```bash
pip install exifread
```

## Usage

To use the script, you need to provide the path to the image file as a command-line argument. As a second argument, you can optionally specify the output type (`int` or `str`). If not provided, the default output type is `str`.

```bash
python main.py <image_path> (int|str)
```

For example:

```bash
python main.py /path/to/image.jpg str
```
This will print the shutter count as an integer:

>  78684

```bash
python main.py /path/to/image.jpg
```

Using none will default to `str`:

> Shutter count: 78684


## Author

**Kolja Nolte** <[kolja.nolte@gmail.com](mailto:kolja.nolte@gmail.com)>

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
