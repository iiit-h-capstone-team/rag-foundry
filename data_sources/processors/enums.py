"""Processing step types."""

from enum import Enum


class ProcessingStepType(str, Enum):
    """Available processing step strategies."""
    DEDUPLICATION = "deduplication"
