"""No-op query transform strategy implementation."""

from rag.modules.query_transform.base import QueryTransformStrategy, QueryTransformResult
from rag.modules.query_transform.registry import query_transform_registry
from rag.modules.query_transform.enums import QueryTransformType
from rag.modules.query_transform.strategies.noop.config import NoOpQueryTransformConfig


@query_transform_registry.register(QueryTransformType.NOOP)
class NoOpQueryTransformStrategy(QueryTransformStrategy):
    """No-op query transform: passes query through unchanged."""

    def __init__(self, config: NoOpQueryTransformConfig):
        super().__init__(config)

    def transform(self, query: str) -> QueryTransformResult:
        """Pass original query through unchanged."""
        return QueryTransformResult(
            dense_queries=[query],
            sparse_queries=[query],
        )
