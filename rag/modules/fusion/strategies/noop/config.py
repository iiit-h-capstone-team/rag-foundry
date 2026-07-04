"""No-op fusion strategy configuration."""

from dataclasses import dataclass
from rag.modules.fusion.config import BaseFusionConfig


@dataclass
class NoOpFusionConfig(BaseFusionConfig):
    """Configuration for no-op fusion strategy."""
    pass
