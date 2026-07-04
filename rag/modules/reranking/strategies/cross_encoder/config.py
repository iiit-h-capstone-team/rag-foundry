"""Cross-encoder reranking strategy configuration."""

from dataclasses import dataclass
from rag.modules.reranking.config import BaseRerankingConfig


@dataclass
class CrossEncoderRerankingConfig(BaseRerankingConfig):
    """Configuration for Cross-encoder reranking strategy."""
    model_name: str = None
