"""TRACe evaluation strategy configuration."""

from dataclasses import dataclass
from evaluation.config import BaseEvaluationConfig


@dataclass
class TRACeEvaluationConfig(BaseEvaluationConfig):
    """Configuration for TRACe evaluation strategy."""
    model: str = None
    temperature: float = 0.0
    max_tokens: int = 2000
