"""Embedding configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from embedding.enums import EmbeddingType


@dataclass
class BaseEmbeddingConfig:
    """Base class for all embedding strategy configurations."""
    pass


@dataclass
class EmbeddingConfig:
    """Embedding section: which strategy plus its own typed config."""
    type: EmbeddingType
    config: Any = None

    def __post_init__(self):
        self.type = EmbeddingType(self.type)
        if self.config is None:
            self.config = {}
