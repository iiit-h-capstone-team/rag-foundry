"""Cohere embedding configuration."""

from dataclasses import dataclass
from typing import Optional

from embedding.config import BaseEmbeddingConfig


@dataclass
class CohereEmbeddingConfig(BaseEmbeddingConfig):
    """Tunables for the Cohere embedding strategy."""
    model_name: Optional[str] = None
    model: Optional[str] = None
    dimension: int = 1024
    input_type: str = "search_document"
