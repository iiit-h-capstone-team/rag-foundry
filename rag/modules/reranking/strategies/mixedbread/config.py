"""MixedBread reranking strategy configuration."""

from dataclasses import dataclass
from rag.modules.reranking.config import BaseRerankingConfig


@dataclass
class MixedBreadRerankingConfig(BaseRerankingConfig):
    """Configuration for MixedBread reranking strategy."""
    model: str = None
    model_name: str = None
    top_n: int = None
