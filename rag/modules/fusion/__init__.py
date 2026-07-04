"""Fusion module with registry-based strategy architecture."""

from rag.modules.fusion.base import FusionStrategy
from rag.modules.fusion.registry import fusion_registry, FusionRegistry
from rag.modules.fusion.enums import FusionType
from rag.modules.fusion.config import FusionConfig, BaseFusionConfig

from rag.modules.fusion.strategies.noop.config import NoOpFusionConfig
from rag.modules.fusion.strategies.noop.strategy import NoOpFusionStrategy

from rag.modules.fusion.strategies.rrf.config import RRFFusionConfig
from rag.modules.fusion.strategies.rrf.strategy import RRFFusionStrategy

from rag.modules.fusion.strategies.weighted_sum.config import WeightedSumFusionConfig
from rag.modules.fusion.strategies.weighted_sum.strategy import WeightedSumFusionStrategy


__all__ = [
    "FusionStrategy",
    "FusionRegistry",
    "fusion_registry",
    "FusionType",
    "FusionConfig",
    "BaseFusionConfig",
    "NoOpFusionConfig",
    "NoOpFusionStrategy",
    "RRFFusionConfig",
    "RRFFusionStrategy",
    "WeightedSumFusionConfig",
    "WeightedSumFusionStrategy",
]
