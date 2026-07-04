"""Voyage reranking strategy configuration."""

from dataclasses import dataclass
from rag.modules.reranking.config import BaseRerankingConfig


@dataclass
class VoyageRerankingConfig(BaseRerankingConfig):
    """Configuration for Voyage reranking strategy."""
    model: str = None
    model_name: str = None
