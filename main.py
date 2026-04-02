"""Thin entry-point script for running the shutter-counter CLI.

This file exists so that the tool can be launched directly with
``python main.py`` from the project root.  All argument parsing and
business logic lives in :mod:`shutter_counter.cli` and
:mod:`shutter_counter.counter`.
"""

from shutter_counter.cli import main

if __name__ == "__main__":
    main()
