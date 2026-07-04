"""Fusion strategy types."""

from enum import Enum


class FusionType(str, Enum):
    """Available fusion strategies."""
    NOOP = "noop"
    RRF = "rrf"
    WEIGHTED_SUM = "weighted_sum"
