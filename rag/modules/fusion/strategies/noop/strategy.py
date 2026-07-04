"""No-op fusion strategy implementation."""

from rag.modules.fusion.base import FusionStrategy
from rag.modules.fusion.registry import fusion_registry
from rag.modules.fusion.enums import FusionType
from rag.modules.fusion.strategies.noop.config import NoOpFusionConfig


@fusion_registry.register(FusionType.NOOP)
class NoOpFusionStrategy(FusionStrategy):
    """No-op fusion: passes first search list through unchanged."""

    def __init__(self, config: NoOpFusionConfig):
        super().__init__(config)

    def fuse(self, search_results: list[list[dict]]) -> list[dict]:
        if not search_results:
            return []
        return list(search_results[0])
