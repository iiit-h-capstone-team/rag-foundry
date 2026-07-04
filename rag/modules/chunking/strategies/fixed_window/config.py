"""Fixed-window chunking configuration."""

from dataclasses import dataclass

from rag.modules.chunking.config import BaseChunkingConfig


@dataclass
class FixedWindowChunkingConfig(BaseChunkingConfig):
    """Tunables for the fixed-window chunking strategy."""
    window_size: int = 256
    overlap: int = 50
