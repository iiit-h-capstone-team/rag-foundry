"""Token-based chunking configuration."""

from dataclasses import dataclass

from rag.modules.chunking.config import BaseChunkingConfig


@dataclass
class TokenChunkingConfig(BaseChunkingConfig):
    """Tunables for the token chunking strategy."""
    max_tokens: int = 200
    overlap_tokens: int = 20
