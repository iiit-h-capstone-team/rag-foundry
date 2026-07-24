"""Chunking module with registry-based strategy architecture."""

from rag.modules.chunking.base import ChunkingStrategy
from rag.modules.chunking.registry import chunking_registry, ChunkingRegistry
from rag.modules.chunking.enums import ChunkingType
from rag.modules.chunking.config import ChunkingConfig, BaseChunkingConfig

from rag.modules.chunking.strategies.sentence.config import SentenceChunkingConfig
from rag.modules.chunking.strategies.sentence.strategy import SentenceChunkingStrategy

from rag.modules.chunking.strategies.fixed_window.config import FixedWindowChunkingConfig
from rag.modules.chunking.strategies.fixed_window.strategy import FixedWindowChunkingStrategy

from rag.modules.chunking.strategies.fixed_word.config import FixedWordChunkingConfig
from rag.modules.chunking.strategies.fixed_word.strategy import FixedWordChunkingStrategy

from rag.modules.chunking.strategies.token.config import TokenChunkingConfig
from rag.modules.chunking.strategies.token.strategy import TokenChunkingStrategy

from rag.modules.chunking.strategies.semantic.config import SemanticChunkingConfig

# Import to trigger decorator registration, but don't expose the class
try:
    from rag.modules.chunking.strategies.semantic.strategy import SemanticChunkingStrategy as _SemanticChunkingStrategy
except ImportError:
    # numpy not available, strategy won't be registered
    pass

# Lazy import for attribute access
def __getattr__(name):
    if name == "SemanticChunkingStrategy":
        from rag.modules.chunking.strategies.semantic.strategy import SemanticChunkingStrategy
        return SemanticChunkingStrategy
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ChunkingStrategy",
    "ChunkingRegistry",
    "chunking_registry",
    "ChunkingType",
    "ChunkingConfig",
    "BaseChunkingConfig",
    "SentenceChunkingConfig",
    "SentenceChunkingStrategy",
    "FixedWindowChunkingConfig",
    "FixedWindowChunkingStrategy",
    "FixedWordChunkingConfig",
    "FixedWordChunkingStrategy",
    "TokenChunkingConfig",
    "TokenChunkingStrategy",
    "SemanticChunkingConfig",
    "SemanticChunkingStrategy",
]
