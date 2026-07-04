"""Search strategy types."""

from enum import Enum


class SearchType(str, Enum):
    """Available search strategies."""
    DENSE = "dense"
    SPARSE = "sparse"
