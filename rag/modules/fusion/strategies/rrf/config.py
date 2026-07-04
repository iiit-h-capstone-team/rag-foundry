"""RRF fusion strategy configuration."""

from dataclasses import dataclass
from rag.modules.fusion.config import BaseFusionConfig


@dataclass
class RRFFusionConfig(BaseFusionConfig):
    """Configuration for reciprocal rank fusion."""
    top_k: int = 5
    k: int = 60
