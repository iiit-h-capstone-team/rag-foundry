"""Query transform module with registry-based strategy architecture."""

from rag.modules.query_transform.base import QueryTransformStrategy, QueryTransformResult
from rag.modules.query_transform.registry import query_transform_registry, QueryTransformRegistry
from rag.modules.query_transform.enums import QueryTransformType
from rag.modules.query_transform.config import QueryTransformConfig, BaseQueryTransformConfig

from rag.modules.query_transform.strategies.noop.config import NoOpQueryTransformConfig
from rag.modules.query_transform.strategies.noop.strategy import NoOpQueryTransformStrategy

from rag.modules.query_transform.strategies.hyde.config import HyDEQueryTransformConfig
from rag.modules.query_transform.strategies.hyde.strategy import HyDEQueryTransformStrategy

from rag.modules.query_transform.strategies.multi_query.config import MultiQueryQueryTransformConfig
from rag.modules.query_transform.strategies.multi_query.strategy import MultiQueryQueryTransformStrategy

from rag.modules.query_transform.strategies.step_back.config import StepBackQueryTransformConfig
from rag.modules.query_transform.strategies.step_back.strategy import StepBackQueryTransformStrategy


__all__ = [
    "QueryTransformStrategy",
    "QueryTransformResult",
    "QueryTransformRegistry",
    "query_transform_registry",
    "QueryTransformType",
    "QueryTransformConfig",
    "BaseQueryTransformConfig",
    "NoOpQueryTransformConfig",
    "NoOpQueryTransformStrategy",
    "HyDEQueryTransformConfig",
    "HyDEQueryTransformStrategy",
    "MultiQueryQueryTransformConfig",
    "MultiQueryQueryTransformStrategy",
    "StepBackQueryTransformConfig",
    "StepBackQueryTransformStrategy",
]
