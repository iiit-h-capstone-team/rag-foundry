"""OpenAI embedding configuration."""

from dataclasses import dataclass
from typing import Optional

from embedding.config import BaseEmbeddingConfig


@dataclass
class OpenAIEmbeddingConfig(BaseEmbeddingConfig):
    """Tunables for the OpenAI embedding strategy."""
    model: Optional[str] = None
    model_name: Optional[str] = None
    dimension: int = 1536
