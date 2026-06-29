from rag.config.config import FusionConfig
from rag.config.enums import FusionType
from rag.retrieval.fusion.noop import NoOpFusionStrategy
from rag.retrieval.fusion.rrf import RRFFusionStrategy
from rag.retrieval.fusion.weighted_sum import WeightedSumFusionStrategy


class FusionFactory:
    
    @staticmethod
    def create_fusion(
        config: FusionConfig,
    ):
        strategies = {
            FusionType.NOOP: lambda: NoOpFusionStrategy(
                config=config.config
            ),
            FusionType.RRF: lambda: RRFFusionStrategy(
                config=config.config
            ),
            FusionType.WEIGHTED_SUM: lambda: WeightedSumFusionStrategy(
                config=config.config
            ),
        }
        return strategies[config.type]()
