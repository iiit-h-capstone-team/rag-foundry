from rag.config.config import QueryTransformConfig
from rag.config.enums import QueryTransformType
from rag.retrieval.query_transform.noop import NoOpQueryTransformStrategy
from rag.retrieval.query_transform.hyde import HyDEQueryTransformStrategy
from rag.retrieval.query_transform.multi_query import MultiQueryQueryTransformStrategy
from rag.retrieval.query_transform.step_back import StepBackQueryTransformStrategy


class QueryTransformFactory:
    
    @staticmethod
    def create_query_transform(
        config: QueryTransformConfig,
        provider=None,
    ):
        strategies = {
            QueryTransformType.NOOP: lambda: NoOpQueryTransformStrategy(
                config=config.config
            ),
            QueryTransformType.HYDE: lambda: HyDEQueryTransformStrategy(
                config=config.config,
                provider=provider
            ),
            QueryTransformType.MULTI_QUERY: lambda: MultiQueryQueryTransformStrategy(
                config=config.config,
                provider=provider
            ),
            QueryTransformType.STEP_BACK: lambda: StepBackQueryTransformStrategy(
                config=config.config,
                provider=provider
            ),
        }
        return strategies[config.type]()