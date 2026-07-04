"""Ollama embedding configuration."""

from dataclasses import dataclass
from typing import Optional

from embedding.config import BaseEmbeddingConfig


@dataclass
class OllamaEmbeddingConfig(BaseEmbeddingConfig):
    """Tunables for the Ollama embedding strategy."""
    model_name: Optional[str] = None
    model: Optional[str] = None
    dimension: int = 768
    base_url: str = "http://localhost:11434"
