"""Sentence chunking configuration."""

from dataclasses import dataclass

from rag.modules.chunking.config import BaseChunkingConfig


@dataclass
class SentenceChunkingConfig(BaseChunkingConfig):
    """Tunables for the sentence chunking strategy."""
    max_words: int = 100
    overlap_sentences: int = 1
