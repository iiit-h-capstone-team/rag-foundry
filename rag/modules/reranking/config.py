"""Reranking configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rag.modules.reranking.enums import RerankingType
from core.config import coerce_config


@dataclass
class BaseRerankingConfig:
    """Base class for all reranking strategy configurations."""
    top_k: int = None


@dataclass
class RerankingConfig:
    """Reranking section: which strategy plus its own typed config."""
    type: RerankingType
    config: Any = None

    def __post_init__(self):
        self.type = RerankingType(self.type)
        if self.config is None:
            self.config = {}
