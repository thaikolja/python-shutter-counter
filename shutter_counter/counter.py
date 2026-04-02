"""Core module for extracting shutter counts from camera image EXIF data.

This module provides the ``ShutterCounter`` class, which reads EXIF metadata
from image files produced by supported Nikon cameras and extracts the shutter
actuation count (the total number of times the camera's mechanical shutter has
been fired).

Supported cameras span most Nikon DSLR models from the D1 series through the
D6, as well as select Z-series mirrorless bodies.

Example usage::

    from shutter_counter.counter import ShutterCounter

    counter = ShutterCounter("photo.jpg")
    result = counter.get_shutter_count()
    print(f"{result.camera_make} {result.camera_model}: {result.shutter_count}")
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import exifread

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supported camera models
# ---------------------------------------------------------------------------

#: Immutable set of Nikon camera model names that are currently supported.
#: Each entry must match the exact string stored in the EXIF ``Image Model``
#: tag (case-sensitive).
SUPPORTED_MODELS = frozenset(
    {
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
        "NIKON D610",
        "NIKON D700",
        "NIKON D300S",
        "NIKON D300",
        "NIKON D200",
        "NIKON D100",
        "NIKON D90",
        "NIKON D70s",
        "NIKON D70",
        "NIKON D60",
        "NIKON D50",
        "NIKON D40x",
        "NIKON D40",
        "NIKON D1X",
        "NIKON D1H",
        "NIKON D1",
        "NIKON D2Xs",
        "NIKON D2X",
        "NIKON D2Hs",
        "NIKON D2H",
        "NIKON D3X",
        "NIKON D3S",
        "NIKON D3",
        "NIKON D4S",
        "NIKON D4",
        "NIKON D5",
    }
)

# ---------------------------------------------------------------------------
# Camera model → EXIF shutter tag mapping
# ---------------------------------------------------------------------------

#: Maps supported camera model names to the primary EXIF MakerNote tag that
#: stores the shutter actuation count for that model.
#:
#: Newer Nikon bodies (D500, D7500, D780, D850, D6, and Z-series) store the
#: value under ``MakerNote ShutterCount``, while older models use
#: ``MakerNote TotalShutterReleases``.
CAMERA_SHUTTER_TAGS = {
    "NIKON D850": "MakerNote ShutterCount",
    "NIKON D780": "MakerNote ShutterCount",
    "NIKON D6": "MakerNote ShutterCount",
    "NIKON D500": "MakerNote ShutterCount",
    "NIKON D7500": "MakerNote ShutterCount",
    "NIKON Z7": "MakerNote ShutterCount",
    "NIKON Z6": "MakerNote ShutterCount",
    "NIKON Z5": "MakerNote ShutterCount",
    "NIKON Z6II": "MakerNote ShutterCount",
    "NIKON Z7II": "MakerNote ShutterCount",
    "NIKON D810": "MakerNote TotalShutterReleases",
    "NIKON D800": "MakerNote TotalShutterReleases",
    "NIKON Df": "MakerNote TotalShutterReleases",
    "NIKON D610": "MakerNote TotalShutterReleases",
    "NIKON D750": "MakerNote TotalShutterReleases",
    "NIKON D700": "MakerNote TotalShutterReleases",
    "NIKON D300S": "MakerNote TotalShutterReleases",
    "NIKON D300": "MakerNote TotalShutterReleases",
    "NIKON D200": "MakerNote TotalShutterReleases",
    "NIKON D100": "MakerNote TotalShutterReleases",
    "NIKON D90": "MakerNote TotalShutterReleases",
    "NIKON D70s": "MakerNote TotalShutterReleases",
    "NIKON D70": "MakerNote TotalShutterReleases",
    "NIKON D60": "MakerNote TotalShutterReleases",
    "NIKON D50": "MakerNote TotalShutterReleases",
    "NIKON D40x": "MakerNote TotalShutterReleases",
    "NIKON D40": "MakerNote TotalShutterReleases",
    "NIKON D1X": "MakerNote TotalShutterReleases",
    "NIKON D1H": "MakerNote TotalShutterReleases",
    "NIKON D1": "MakerNote TotalShutterReleases",
    "NIKON D2Xs": "MakerNote TotalShutterReleases",
    "NIKON D2X": "MakerNote TotalShutterReleases",
    "NIKON D2Hs": "MakerNote TotalShutterReleases",
    "NIKON D2H": "MakerNote TotalShutterReleases",
    "NIKON D3X": "MakerNote TotalShutterReleases",
    "NIKON D3S": "MakerNote TotalShutterReleases",
    "NIKON D3": "MakerNote TotalShutterReleases",
    "NIKON D4S": "MakerNote TotalShutterReleases",
    "NIKON D4": "MakerNote TotalShutterReleases",
    "NIKON D5": "MakerNote TotalShutterReleases",
    "NIKON D3500": "MakerNote TotalShutterReleases",
}

# ---------------------------------------------------------------------------
# Fallback tags
# ---------------------------------------------------------------------------

#: Ordered list of EXIF tag names to try as fallbacks when the primary tag for
#: a given camera model is absent from the image metadata.  Tags are tried in
#: the order listed until one yields a value.
FALLBACK_TAGS = [
    "MakerNote ShutterCount",
    "MakerNote TotalShutterReleases",
    "MakerNote ImageNumber",
    "ShutterCount",
    "TotalShutterReleases",
]

# ---------------------------------------------------------------------------
# Public data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ShutterCountResult:
    """Holds the result of a successful shutter count extraction.

    Attributes:
        camera_make: The camera manufacturer as stored in the EXIF
            ``Image Make`` tag (e.g. ``"NIKON CORPORATION"``).
        camera_model: The camera model as stored in the EXIF ``Image Model``
            tag (e.g. ``"NIKON D850"``).
        shutter_count: The shutter actuation count, either as an ``int`` or
            a ``str`` depending on the ``output_type`` requested.
    """

    camera_make: str
    camera_model: str
    shutter_count: int | str


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class ShutterCounterError(Exception):
    """Base exception for all errors raised by :class:`ShutterCounter`."""


class UnsupportedCameraError(ShutterCounterError):
    """Raised when the camera model identified in the image is not supported."""


class ShutterCountNotFoundError(ShutterCounterError):
    """Raised when no shutter count tag could be found in the image EXIF data."""


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------


class ShutterCounter:
    """Extract shutter count from EXIF data of supported Nikon cameras.

    Args:
        image_path: Path to a JPEG or NEF image file.  Accepts either a
            string or a :class:`pathlib.Path` object.
        shutter_tag: Optional override for the EXIF tag name to read the
            shutter count from.  When provided, this tag is tried first
            before falling back to :data:`FALLBACK_TAGS`.

    Example::

        counter = ShutterCounter("photo.jpg")
        result = counter.get_shutter_count()
        print(result.shutter_count)
    """

    def __init__(self, image_path: str | Path, shutter_tag: str | None = None) -> None:
        self.image_path = Path(image_path)
        """Resolved path to the image file."""
        self.shutter_tag = shutter_tag
        """Optional custom EXIF tag name for the shutter count."""

    def _get_tags_to_try(self, camera_model: str) -> list[str]:
        """Return the ordered list of EXIF tags to attempt for *camera_model*.

        If a custom ``shutter_tag`` was supplied at construction, it is tried
        first.  Otherwise the model-specific primary tag from
        :data:`CAMERA_SHUTTER_TAGS` is used.  In both cases the full
        :data:`FALLBACK_TAGS` list is appended so that missing or renamed tags
        are handled gracefully.

        Args:
            camera_model: The camera model string from the EXIF ``Image Model``
                tag.

        Returns:
            An ordered list of EXIF tag names to try.
        """
        if self.shutter_tag:
            return [self.shutter_tag] + FALLBACK_TAGS

        primary_tag = CAMERA_SHUTTER_TAGS.get(camera_model)
        if primary_tag:
            return [primary_tag] + FALLBACK_TAGS

        return FALLBACK_TAGS

    @staticmethod
    def _clean_make(raw_make: str) -> str:
        """Return a human-friendly manufacturer name from the raw EXIF value.

        Nikon stores the make as ``"NIKON CORPORATION"``; this method trims
        the redundant ``" CORPORATION"`` suffix.  For any other manufacturer
        the raw value is returned unchanged.

        Args:
            raw_make: The raw ``Image Make`` EXIF tag value.

        Returns:
            A cleaned manufacturer name (e.g. ``"NIKON"``).
        """
        return raw_make.replace(" CORPORATION", "")

    @staticmethod
    def _clean_model(raw_model: str) -> str:
        """Return a human-friendly model name by stripping the manufacturer prefix.

        Nikon stores the model as ``"NIKON D850"``; this method removes the
        leading ``"NIKON "`` so the result is just ``"D850"``.  For cameras
        that don't follow this pattern the raw value is returned unchanged.

        Args:
            raw_model: The raw ``Image Model`` EXIF tag value.

        Returns:
            A cleaned model name (e.g. ``"D850"``).
        """
        for prefix in ("NIKON ", "Nikon "):
            if raw_model.startswith(prefix):
                return raw_model[len(prefix) :]
        return raw_model

    def get_shutter_count(
        self,
        output_type: Literal["int", "str"] = "int",
    ) -> ShutterCountResult:
        """Read the image EXIF data and return the shutter count.

        Args:
            output_type: Controls the type of ``shutter_count`` in the
                returned :class:`ShutterCountResult`.  ``"int"`` (the default)
                converts the value to an integer; ``"str"`` returns the raw
                string from the EXIF tag.

        Returns:
            A :class:`ShutterCountResult` containing the camera make, camera
            model, and shutter count.

        Raises:
            FileNotFoundError: If *image_path* does not point to an existing
                file.
            ShutterCounterError: If the image cannot be read or the shutter
                count value cannot be converted to ``int``.
            UnsupportedCameraError: If the camera model is not in
                :data:`SUPPORTED_MODELS`.
            ShutterCountNotFoundError: If none of the attempted EXIF tags
                contain a shutter count value.
        """
        if not self.image_path.is_file():
            raise FileNotFoundError(f"Image file not found: {self.image_path}")

        try:
            with open(self.image_path, "rb") as f:
                tags = exifread.process_file(f, details=True)
        except OSError as e:
            raise ShutterCounterError(f"Could not read image: {e}") from e

        camera_model = str(tags.get("Image Model", "")).strip()
        if camera_model not in SUPPORTED_MODELS:
            raise UnsupportedCameraError(f"Unsupported camera model: {camera_model}")

        camera_make = str(tags.get("Image Make", "")).strip()

        tags_to_try = self._get_tags_to_try(camera_model)

        shutter_tag_data = None
        used_tag = None
        for tag in tags_to_try:
            shutter_tag_data = tags.get(tag)
            if shutter_tag_data:
                used_tag = tag
                break

        if not shutter_tag_data:
            logger.warning(
                "Shutter count not found in EXIF data. Tried tags: %s",
                ", ".join(tags_to_try),
            )
            raise ShutterCountNotFoundError(
                f"Shutter count not found for {camera_model}. Tried tags: {', '.join(tags_to_try)}."
            )

        logger.debug("Found shutter count using tag: %s", used_tag)

        shutter_count_str = str(shutter_tag_data).strip()
        shutter_count: int | str
        if output_type == "int":
            try:
                shutter_count = int(shutter_count_str)
            except ValueError as e:
                raise ShutterCounterError(
                    f"Cannot convert shutter count '{shutter_count_str}' to int."
                ) from e
        else:
            shutter_count = shutter_count_str

        return ShutterCountResult(
            camera_make=self._clean_make(camera_make),
            camera_model=self._clean_model(camera_model),
            shutter_count=shutter_count,
        )
