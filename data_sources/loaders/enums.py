"""Dataset loader strategy types."""

from enum import Enum


class LoaderType(str, Enum):
    """Available dataset loader strategies."""
    HUGGINGFACE = "huggingface"
