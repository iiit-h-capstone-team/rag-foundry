"""Cohere reranking strategy configuration."""

from dataclasses import dataclass
from rag.modules.reranking.config import BaseRerankingConfig


@dataclass
class CohereRerankingConfig(BaseRerankingConfig):
    """Configuration for Cohere reranking strategy."""
    model: str = "rerank-english-v2.0"
    top_n: int = None
