"""Reranking strategy types."""

from enum import Enum


class RerankingType(str, Enum):
    """Available reranking strategies."""
    COHERE = "cohere"
    JINA = "jina"
    CROSS_ENCODER = "cross_encoder"
    MIXEDBREAD = "mixedbread"
    VOYAGE = "voyage"
