"""Evaluation strategy types."""

from enum import Enum


class EvaluationType(str, Enum):
    """Available evaluation strategies."""
    TRACE = "trace"
