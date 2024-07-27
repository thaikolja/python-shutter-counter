# Python Shutter Counter

![GitLab Release](https://img.shields.io/gitlab/v/release/thaikolja%2Fpython-shutter-counter) [![Python 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![GitHub stars](https://img.shields.io/github/stars/shutter-counter/python-shutter-counter.svg)](https://github.com/shutter-counter/python-shutter-counter)

A Python script to read the EXIF data from an image file and **extract the shutter count** of a DSLR camera.

## Description

This script is designed to work with Nikon **D850**, **D810**, and **D800** camera models. Other models can be added easily in the main class. The script uses the `exifread` library to parse the EXIF data from the image file and extract the shutter count. Check out the [exifread documentation](https://pypi.org/project/ExifRead/) for more information on how EXIF data is parsed.

## Features

* Extracts the shutter count from the EXIF data of an image file
* Supports Nikon **D850**, **D810**, and **D800** camera models
* Can output the shutter count as an integer or a string
* Provides error handling for invalid image files, unsupported camera models, and other issues

## Installation Instructions

1. **Ensure you have Python 3 installed.** You can download it from the [official Python website](https://www.python.org/downloads/)
2. **Install the required `exifread`** library using the  `pip` command. [Official documentation](https://pip.pypa.io/en/stable/user_guide/)

```bash
pip install exifread
```

Clone or download the Shutter Counter repository to your local machine.

### Download via Git

```bash
git clone https://gitlab.com/thaikolja/python-shutter-counter.git
```

### Download as a .zip File

Click [here to download the latest version](https://gitlab.com/thaikolja/python-shutter-counter/-/archive/main/python-shutter-counter-main.zip).

## Usage Examples

To use the script, simply run it from the command line and provide the path to the image file as an argument:

```bash
python main.py /path/to/image.jpg
```

This will output the shutter count as a string:

```
Shutter count: 78684
```

You can also specify the output type as an integer by adding the `int` argument:

```bash
python main.py /path/to/image.jpg int
```

This will output the shutter count as an integer:

```
78684
```

Check out the [Python documentation](https://docs.python.org/3/tutorial/interpreter.html) for more information on running Python scripts from the command line.

## Contribution Guidelines

Pull requests are welcome! If you'd like to contribute to the project, please fork the repository and submit a pull request with your changes. Make sure to include a clear description of your changes and any relevant testing or documentation updates. Check out [this guide](https://nira.com/gitlab-pull-request/) for more information on pull requests.

## Testing Instructions

To test the script, simply run it with a valid image file and verify that the output is correct. You can also test the script with invalid image files or unsupported camera models to ensure that it handles errors correctly.

## License

This project is licensed under the MIT License. For details, see the [LICENSE file](LICENSE). For more information on the MIT License, check out the [Open Source Initiative](https://opensource.org/licenses/MIT).

## Author

* **Kolja Nolte** [<kolja.nolte@gmail.com>](mailto:kolja.nolte@gmail.com)
