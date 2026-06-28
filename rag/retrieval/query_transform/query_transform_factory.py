from rag.config.config import QueryTransformConfig
from rag.config.enums import QueryTransformType
from rag.retrieval.query_transform.noop import NoOpQueryTransformStrategy


class QueryTransformFactory:
    
    @staticmethod
    def create_query_transform(
        config: QueryTransformConfig,
    ):
        strategies = {
            QueryTransformType.NOOP: lambda: NoOpQueryTransformStrategy(
                config=config.config
            ),
        }
        return strategies[config.type]()