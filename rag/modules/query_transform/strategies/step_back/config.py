"""Step-Back query transform strategy configuration."""

from dataclasses import dataclass
from rag.modules.query_transform.config import BaseQueryTransformConfig


@dataclass
class StepBackQueryTransformConfig(BaseQueryTransformConfig):
    """Configuration for Step-Back query transform strategy."""
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.3
    max_tokens: int = 128
