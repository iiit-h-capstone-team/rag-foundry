"""Generation configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Union

from rag.modules.generation.enums import GenerationType
from core.config import coerce_config


@dataclass
class BaseGenerationConfig:
    """Base class for all generation strategy configurations."""
    pass


@dataclass
class GenerationConfig:
    """Generation section: which strategy plus its own typed config."""
    strategy: Union[str, GenerationType] = GenerationType.DEFAULT
    provider: str = None
    config: Any = None

    def __post_init__(self):
        self.strategy = GenerationType(self.strategy)
        if self.config is None:
            self.config = {}
