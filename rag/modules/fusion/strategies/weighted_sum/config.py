"""Weighted sum fusion strategy configuration."""

from dataclasses import dataclass, field
from rag.modules.fusion.config import BaseFusionConfig


@dataclass
class WeightedSumFusionConfig(BaseFusionConfig):
    """Configuration for weighted score fusion."""
    top_k: int = 5
    weights: list = field(default_factory=list)
