"""Generation module with registry-based strategy architecture."""

from rag.modules.generation.base import GenerationStrategy
from rag.modules.generation.registry import generation_registry, GenerationRegistry
from rag.modules.generation.enums import GenerationType
from rag.modules.generation.config import GenerationConfig, BaseGenerationConfig

from rag.modules.generation.strategies.default.config import DefaultGenerationConfig
from rag.modules.generation.strategies.default.strategy import DefaultGenerationStrategy


__all__ = [
    "GenerationStrategy",
    "GenerationRegistry",
    "generation_registry",
    "GenerationType",
    "GenerationConfig",
    "BaseGenerationConfig",
    "DefaultGenerationConfig",
    "DefaultGenerationStrategy",
]
