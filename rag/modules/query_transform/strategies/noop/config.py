"""No-op query transform strategy configuration."""

from dataclasses import dataclass
from rag.modules.query_transform.config import BaseQueryTransformConfig


@dataclass
class NoOpQueryTransformConfig(BaseQueryTransformConfig):
    """Configuration for no-op query transform strategy."""
    pass
