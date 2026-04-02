"""Tests for the :mod:`shutter_counter.cli` module.

Covers argument parsing, image path resolution, and output formatting.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from shutter_counter.cli import _resolve_image_path


class TestResolveImagePath:
    """Tests for the ``_resolve_image_path`` helper."""

    def test_flag_takes_priority_over_positional(self):
        """When both are given, ``--input`` wins over the positional argument."""
        result = _resolve_image_path("positional.jpg", "flag.jpg")
        assert result == "flag.jpg"

    def test_flag_only(self):
        """Only ``--input`` provided returns the flag value."""
        result = _resolve_image_path(None, "flag.jpg")
        assert result == "flag.jpg"

    def test_positional_only_valid_file(self):
        """A positional argument that points to an existing file is accepted."""
        with patch.object(Path, "is_file", return_value=True):
            result = _resolve_image_path("photo.jpg", None)
            assert result == "photo.jpg"

    def test_positional_only_invalid_file(self):
        """A positional argument that is not a file causes ``sys.exit``."""
        with patch.object(Path, "is_file", return_value=False), pytest.raises(SystemExit):
            _resolve_image_path("nonexistent.jpg", None)

    def test_no_arguments(self):
        """When neither argument is given, ``sys.exit`` is called."""
        with pytest.raises(SystemExit):
            _resolve_image_path(None, None)
