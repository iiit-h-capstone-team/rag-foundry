"""Chunking configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Union

from rag.modules.chunking.enums import ChunkingType
from core.config import coerce_config


@dataclass
class BaseChunkingConfig:
    """Base class for all chunking strategy configurations."""
    pass


@dataclass
class ChunkingConfig:
    """Chunking section: which strategy plus its own typed config."""
    type: ChunkingType
    config: Any = None

    def __post_init__(self):
        self.type = ChunkingType(self.type)
        if self.config is None:
            self.config = {}
