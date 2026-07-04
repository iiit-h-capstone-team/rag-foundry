"""Jina reranking strategy configuration."""

from dataclasses import dataclass
from rag.modules.reranking.config import BaseRerankingConfig


@dataclass
class JinaRerankingConfig(BaseRerankingConfig):
    """Configuration for Jina reranking strategy."""
    model: str = "jina-reranker-v1-base-en"
    top_n: int = None
