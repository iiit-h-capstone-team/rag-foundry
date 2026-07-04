"""Voyage AI embedding configuration."""

from dataclasses import dataclass
from typing import Optional

from embedding.config import BaseEmbeddingConfig


@dataclass
class VoyageEmbeddingConfig(BaseEmbeddingConfig):
    """Tunables for the Voyage AI embedding strategy."""
    model_name: Optional[str] = None
    model: Optional[str] = None
    dimension: int = 1024
    input_type: Optional[str] = None
