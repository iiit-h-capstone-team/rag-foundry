"""Evaluation configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from evaluation.enums import EvaluationType


@dataclass
class BaseEvaluationConfig:
    """Base class for all evaluation strategy configurations."""
    pass


@dataclass
class EvaluationConfig:
    """Evaluation section: which strategy plus its own typed config."""
    type: EvaluationType
    provider: str = None
    config: Any = None

    def __post_init__(self):
        self.type = EvaluationType(self.type)
        if self.config is None:
            self.config = {}
