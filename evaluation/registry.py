"""Evaluation strategy registry."""

from core.registry import BaseRegistry
from evaluation.base import EvaluationStrategy


class EvaluationRegistry(BaseRegistry[EvaluationStrategy]):
    """Registry for evaluation strategy plugins."""
    pass


evaluation_registry = EvaluationRegistry()
