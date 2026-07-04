"""Vector store configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from vectorstore.enums import VectorStoreType


@dataclass
class BaseVectorStoreConfig:
    """Base class for all vector store strategy configurations."""
    pass


@dataclass
class VectorStoreConfig:
    """Vector store section: which strategy plus its own typed config."""
    type: VectorStoreType
    config: Any = None

    def __post_init__(self):
        self.type = VectorStoreType(self.type)
        if self.config is None:
            self.config = {}
