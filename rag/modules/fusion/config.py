"""Fusion configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from rag.modules.fusion.enums import FusionType


@dataclass
class BaseFusionConfig:
    """Base class for all fusion strategy configurations."""
    pass


@dataclass
class FusionConfig:
    """Fusion stage: which strategy plus its own typed config."""
    type: FusionType
    config: Any = None

    def __post_init__(self):
        self.type = FusionType(self.type)
        if self.config is None:
            self.config = {}
