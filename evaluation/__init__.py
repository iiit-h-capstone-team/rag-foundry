"""Evaluation module with registry-based strategy architecture.

This is a standalone benchmarking tool, not part of the RAG pipeline.
Evaluation reads JSONL files containing generation results and scores them offline.
"""

from evaluation.base import EvaluationStrategy
from evaluation.registry import evaluation_registry, EvaluationRegistry
from evaluation.enums import EvaluationType
from evaluation.config import EvaluationConfig, BaseEvaluationConfig

from evaluation.strategies.trace.config import TRACeEvaluationConfig
from evaluation.strategies.trace.strategy import TRACeEvaluationStrategy


__all__ = [
    "EvaluationStrategy",
    "EvaluationRegistry",
    "evaluation_registry",
    "EvaluationType",
    "EvaluationConfig",
    "BaseEvaluationConfig",
    "TRACeEvaluationConfig",
    "TRACeEvaluationStrategy",
]
