"""Fixed-word chunking configuration."""

from dataclasses import dataclass

from rag.modules.chunking.config import BaseChunkingConfig


@dataclass
class FixedWordChunkingConfig(BaseChunkingConfig):
    """Tunables for the fixed-word chunking strategy."""
    max_words: int = 200
    overlap_words: int = 20
