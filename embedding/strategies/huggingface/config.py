"""HuggingFace embedding configuration."""

from dataclasses import dataclass
from typing import Optional

from embedding.config import BaseEmbeddingConfig


@dataclass
class HuggingFaceEmbeddingConfig(BaseEmbeddingConfig):
    """Tunables for the HuggingFace Inference embedding strategy."""
    model_name: Optional[str] = None
    model: Optional[str] = None
    dimension: int = 768
    api_url: Optional[str] = None
