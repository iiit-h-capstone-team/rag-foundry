"""Semantic chunking configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rag.modules.chunking.config import BaseChunkingConfig
from core.config import coerce_config

if TYPE_CHECKING:
    from embedding.config import EmbeddingConfig


@dataclass
class SemanticChunkingConfig(BaseChunkingConfig):
    """Tunables for the semantic chunking strategy."""
    embedding: EmbeddingConfig = None
    max_words: int = 256
    similarity_threshold: float = 0.8
    overlap_sentences: int = 1
    similarity_window: int = 5

    def __post_init__(self):
        if self.embedding is not None:
            from embedding.config import EmbeddingConfig
            self.embedding = coerce_config(self.embedding, EmbeddingConfig)
