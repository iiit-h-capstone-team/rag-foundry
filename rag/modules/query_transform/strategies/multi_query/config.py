"""MultiQuery query transform strategy configuration."""

from dataclasses import dataclass
from rag.modules.query_transform.config import BaseQueryTransformConfig


@dataclass
class MultiQueryQueryTransformConfig(BaseQueryTransformConfig):
    """Configuration for MultiQuery query transform strategy."""
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    num_queries: int = 4
    max_tokens: int = 128
