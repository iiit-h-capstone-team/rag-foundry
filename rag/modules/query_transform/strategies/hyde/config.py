"""HyDE query transform strategy configuration."""

from dataclasses import dataclass
from rag.modules.query_transform.config import BaseQueryTransformConfig


@dataclass
class HyDEQueryTransformConfig(BaseQueryTransformConfig):
    """Configuration for HyDE query transform strategy."""
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.2
    max_tokens: int = 256
