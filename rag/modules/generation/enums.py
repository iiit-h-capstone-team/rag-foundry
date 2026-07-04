"""Generation strategy types."""

from enum import Enum


class GenerationType(str, Enum):
    """Available generation strategies."""
    DEFAULT = "default"
