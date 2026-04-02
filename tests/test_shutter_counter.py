"""Tests for the :mod:`shutter_counter.counter` module.

Covers initialisation, error handling, and successful shutter count
extraction across multiple supported Nikon camera models.
"""

from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from shutter_counter.counter import (
    ShutterCounter,
    ShutterCounterError,
    ShutterCountNotFoundError,
    ShutterCountResult,
    UnsupportedCameraError,
)


class TestShutterCounterInit:
    """Tests for :class:`ShutterCounter` construction."""

    def test_init_with_string_path(self):
        """A string image path is converted to a :class:`Path` object."""
        counter = ShutterCounter("/fake/path.jpg")
        assert counter.image_path == Path("/fake/path.jpg")

    def test_init_with_path_object(self):
        """A :class:`Path` object is stored as-is."""
        counter = ShutterCounter(Path("/fake/path.jpg"))
        assert counter.image_path == Path("/fake/path.jpg")

    def test_init_default_shutter_tag(self):
        """When no ``shutter_tag`` is given the attribute is ``None``."""
        counter = ShutterCounter("/fake/path.jpg")
        assert counter.shutter_tag is None

    def test_init_custom_shutter_tag(self):
        """A custom ``shutter_tag`` is stored on the instance."""
        counter = ShutterCounter("/fake/path.jpg", shutter_tag="CustomTag")
        assert counter.shutter_tag == "CustomTag"


class TestGetShutterCount:
    """Tests for :meth:`ShutterCounter.get_shutter_count`."""

    def _mock_tags(self, model: str, shutter_count: str | None = None):
        """Build a minimal dict of mocked EXIF tags.

        Args:
            model: The camera model string to return for ``Image Model``.
            shutter_count: Optional shutter count value for the primary tag.
                When ``None`` the tag is omitted to simulate a missing value.

        Returns:
            A dictionary suitable as a return value for
            ``exifread.process_file``.
        """
        tags = {"Image Model": MagicMock(__str__=lambda self: model)}
        if shutter_count is not None:
            tags["MakerNote TotalShutterReleases"] = MagicMock(__str__=lambda self: shutter_count)
        return tags

    def test_file_not_found(self):
        """A missing image file raises :exc:`FileNotFoundError`."""
        counter = ShutterCounter("/nonexistent/file.jpg")
        with pytest.raises(FileNotFoundError, match="not found"):
            counter.get_shutter_count()

    def test_unsupported_camera_model(self):
        """An unknown camera model raises :exc:`UnsupportedCameraError`."""
        mock_tags = self._mock_tags("Canon EOS 5D")
        with (
            patch("shutter_counter.counter.exifread.process_file", return_value=mock_tags),
            patch.object(Path, "is_file", return_value=True),
            patch("builtins.open", mock_open()),
        ):
            counter = ShutterCounter("/fake/path.jpg")
            with pytest.raises(UnsupportedCameraError, match="Unsupported camera model"):
                counter.get_shutter_count()

    def test_shutter_count_not_found(self):
        """A supported camera with no shutter tag raises :exc:`ShutterCountNotFoundError`."""
        mock_tags = self._mock_tags("NIKON D850")
        with (
            patch("shutter_counter.counter.exifread.process_file", return_value=mock_tags),
            patch.object(Path, "is_file", return_value=True),
            patch("builtins.open", mock_open()),
        ):
            counter = ShutterCounter("/fake/path.jpg")
            with pytest.raises(ShutterCountNotFoundError, match="not found"):
                counter.get_shutter_count()

    def test_get_shutter_count_as_int(self):
        """The default ``output_type`` returns an integer in the result."""
        mock_tags = self._mock_tags("NIKON D850", shutter_count="12345")
        with (
            patch("shutter_counter.counter.exifread.process_file", return_value=mock_tags),
            patch.object(Path, "is_file", return_value=True),
            patch("builtins.open", mock_open()),
        ):
            counter = ShutterCounter("/fake/path.jpg")
            result = counter.get_shutter_count()
            assert isinstance(result, ShutterCountResult)
            assert result.shutter_count == 12345

    def test_get_shutter_count_as_str(self):
        """``output_type='str'`` returns the raw string value."""
        mock_tags = self._mock_tags("NIKON D750", shutter_count="9876")
        with (
            patch("shutter_counter.counter.exifread.process_file", return_value=mock_tags),
            patch.object(Path, "is_file", return_value=True),
            patch("builtins.open", mock_open()),
        ):
            counter = ShutterCounter("/fake/path.jpg")
            result = counter.get_shutter_count(output_type="str")
            assert result.shutter_count == "9876"

    def test_invalid_shutter_count_for_int(self):
        """A non-numeric shutter value raises :exc:`ShutterCounterError`."""
        mock_tags = self._mock_tags("NIKON D850", shutter_count="not_a_number")
        with (
            patch("shutter_counter.counter.exifread.process_file", return_value=mock_tags),
            patch.object(Path, "is_file", return_value=True),
            patch("builtins.open", mock_open()),
        ):
            counter = ShutterCounter("/fake/path.jpg")
            with pytest.raises(ShutterCounterError, match="Cannot convert"):
                counter.get_shutter_count()

    def test_io_error_reading_file(self):
        """An I/O error while opening the file raises :exc:`ShutterCounterError`."""
        with (
            patch.object(Path, "is_file", return_value=True),
            patch("builtins.open", mock_open()) as mock_file,
        ):
            mock_file.side_effect = OSError("Permission denied")
            counter = ShutterCounter("/fake/path.jpg")
            with pytest.raises(ShutterCounterError, match="Could not read"):
                counter.get_shutter_count()

    def test_result_contains_camera_make_and_model(self):
        """The returned :class:`ShutterCountResult` includes make and model."""
        mock_tags = {
            "Image Make": MagicMock(__str__=lambda self: "NIKON CORPORATION"),
            "Image Model": MagicMock(__str__=lambda self: "NIKON D850"),
            "MakerNote ShutterCount": MagicMock(__str__=lambda self: "42"),
        }
        with (
            patch("shutter_counter.counter.exifread.process_file", return_value=mock_tags),
            patch.object(Path, "is_file", return_value=True),
            patch("builtins.open", mock_open()),
        ):
            counter = ShutterCounter("/fake/path.jpg")
            result = counter.get_shutter_count()
            assert result.camera_make == "NIKON"
            assert result.camera_model == "D850"
            assert result.shutter_count == 42


class TestSupportedModels:
    """Parametrised tests verifying all listed models are recognised."""

    @pytest.mark.parametrize(
        "model",
        [
            "NIKON D6",
            "NIKON D850",
            "NIKON D780",
            "NIKON D500",
            "NIKON D7500",
            "NIKON D3500",
            "NIKON D750",
            "NIKON D810",
            "NIKON D800",
            "NIKON Df",
        ],
    )
    def test_supported_models_recognized(self, model):
        """Each supported model returns a valid shutter count."""
        mock_tags = {
            "Image Make": MagicMock(__str__=lambda self: "NIKON CORPORATION"),
            "Image Model": MagicMock(__str__=lambda self: model),
            "MakerNote TotalShutterReleases": MagicMock(__str__=lambda self: "100"),
        }
        with (
            patch("shutter_counter.counter.exifread.process_file", return_value=mock_tags),
            patch.object(Path, "is_file", return_value=True),
            patch("builtins.open", mock_open()),
        ):
            counter = ShutterCounter("/fake/path.jpg")
            result = counter.get_shutter_count()
            assert result.shutter_count == 100
