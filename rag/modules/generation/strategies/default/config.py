"""Default generation strategy configuration."""

from dataclasses import dataclass
from rag.modules.generation.config import BaseGenerationConfig


@dataclass
class DefaultGenerationConfig(BaseGenerationConfig):
    """Configuration for default generation strategy."""
    model: str = None
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: str = None
    user_prompt: str = None
