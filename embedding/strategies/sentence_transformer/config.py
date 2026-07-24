"""Sentence Transformer embedding configuration."""

from dataclasses import dataclass
from typing import Optional

from embedding.config import BaseEmbeddingConfig


@dataclass
class SentenceTransformerEmbeddingConfig(BaseEmbeddingConfig):
    """Tunables for the sentence-transformer embedding strategy."""
    model_name: Optional[str] = None
    model: Optional[str] = None
    dimension: int = 768
    query_instruction: Optional[str] = None
