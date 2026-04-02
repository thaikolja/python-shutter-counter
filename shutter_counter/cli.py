"""Command-line interface for the shutter-counter tool.

This module provides the `main()` entry point used when the package is
invoked from the command line (e.g. `python -m shutter_counter.cli` or
via the `shutter-counter` console script installed by pip).

The CLI parses command-line arguments, calls :class:`~shutter_counter.counter.ShutterCounter`,
and prints the result in either a human-readable sentence or a clean
number-only format.

Default output:

    Shutter count for NIKON D850 is 83,002

With `--clean` / `-c`:

    83,002

All standard argparse flags are supported:

* `-h`, `--help` – show help message and exit
* `image` – optional positional argument for the image file path
* `-i`, `--input` – explicit image file path (overrides positional argument)
* `-c`, `--clean` – print only the shutter count number
* `-v`, `--verbose` – enable debug logging to stderr
"""

import argparse
import logging
import sys
from pathlib import Path

from shutter_counter.counter import (
    ShutterCounter,
    ShutterCounterError,
    ShutterCountNotFoundError,
    UnsupportedCameraError,
)

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        A fully configured :class:`argparse.ArgumentParser` with all CLI
        options defined.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="shutter-counter",
        description="Extract the shutter actuation count from Nikon camera images.",
        epilog=(
            "Examples:\n"
            "  shutter-counter photo.jpg          # positional argument\n"
            "  shutter-counter -i photo.jpg       # explicit flag\n"
            "  shutter-counter photo.jpg -c       # clean output\n"
        ),
    )
    parser.add_argument(
        "image",
        nargs="?",
        default=None,
        help="Path to the image file (JPEG or NEF) to read shutter count from.",
    )
    parser.add_argument(
        "-i",
        "--input",
        default=None,
        help="Path to the image file (overrides positional argument if both are given).",
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        default=False,
        help="Output only the shutter count number, without any additional text.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose (debug) logging output to stderr.",
    )
    return parser


def _resolve_image_path(positional: str | None, flag: str | None) -> str:
    """Determine which image path to use based on CLI arguments.

    Priority:
        1. `--input` / `-i` flag (if provided)
        2. Positional `image` argument (if it points to an existing file)

    Args:
        positional: The value of the positional `image` argument, or `None`.
        flag: The value of the `--input` flag, or `None`.

    Returns:
        The resolved image path as a string.

    Raises:
        SystemExit: If no valid image path could be determined.
    """
    if flag is not None:
        return flag

    if positional is not None and Path(positional).is_file():
        return positional

    print("Error: No image file specified. Provide a path as the first argument or use --input.")
    sys.exit(1)


def main() -> None:
    """CLI entry point.

    Parses command-line arguments, reads the specified image file, extracts
    the shutter count via :class:`~shutter_counter.counter.ShutterCounter`,
    and prints the result.

    Image path resolution order:
        1. `--input` / `-i` flag (highest priority)
        2. First positional argument (if it is a valid file path)

    Exit codes:
        0 – Success.
        1 – An error occurred (unsupported camera, shutter count not found,
            file not readable, etc.).
    """
    parser: argparse.ArgumentParser = _build_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

    image_path = _resolve_image_path(args.image, args.input)

    try:
        counter: ShutterCounter = ShutterCounter(image_path)
        result = counter.get_shutter_count()

        shutter_display = (
            f"{result.shutter_count:,}"
            if isinstance(result.shutter_count, int)
            else result.shutter_count
        )

        if args.clean:
            print(shutter_display)
        else:
            print(
                f"Shutter count for {result.camera_make} {result.camera_model} is {shutter_display}"
            )
    except UnsupportedCameraError as e:
        logger.error(e)
        sys.exit(1)
    except ShutterCountNotFoundError as e:
        logger.warning(e)
        sys.exit(1)
    except (FileNotFoundError, ShutterCounterError) as e:
        logger.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
