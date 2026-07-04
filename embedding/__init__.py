"""Embedding module with registry-based strategy architecture."""

from embedding.base import EmbeddingStrategy
from embedding.registry import embedding_registry, EmbeddingRegistry
from embedding.enums import EmbeddingType
from embedding.config import EmbeddingConfig, BaseEmbeddingConfig

from embedding.strategies.sentence_transformer.config import SentenceTransformerEmbeddingConfig

from embedding.strategies.openai.config import OpenAIEmbeddingConfig
from embedding.strategies.openai.strategy import OpenAIEmbeddingStrategy

from embedding.strategies.ollama.config import OllamaEmbeddingConfig
from embedding.strategies.ollama.strategy import OllamaEmbeddingStrategy

from embedding.strategies.cohere.config import CohereEmbeddingConfig
from embedding.strategies.cohere.strategy import CohereEmbeddingStrategy

from embedding.strategies.voyage.config import VoyageEmbeddingConfig
from embedding.strategies.voyage.strategy import VoyageEmbeddingStrategy

from embedding.strategies.huggingface.config import HuggingFaceEmbeddingConfig
from embedding.strategies.huggingface.strategy import HuggingFaceEmbeddingStrategy

from embedding.strategies.medcpt.config import MedCPTEmbeddingConfig

# Import to trigger decorator registration, but don't expose the classes
try:
    from embedding.strategies.sentence_transformer.strategy import (
        SentenceTransformerEmbeddingStrategy as _SentenceTransformerEmbeddingStrategy,
    )
except ImportError:
    # sentence_transformers not available, strategy won't be registered
    pass

try:
    from embedding.strategies.medcpt.strategy import (
        MedCPTEmbeddingStrategy as _MedCPTEmbeddingStrategy,
    )
except ImportError:
    # numpy not available, strategy won't be registered
    pass


# Lazy imports for attribute access
def __getattr__(name):
    if name == "SentenceTransformerEmbeddingStrategy":
        from embedding.strategies.sentence_transformer.strategy import (
            SentenceTransformerEmbeddingStrategy,
        )
        return SentenceTransformerEmbeddingStrategy
    elif name == "MedCPTEmbeddingStrategy":
        from embedding.strategies.medcpt.strategy import MedCPTEmbeddingStrategy
        return MedCPTEmbeddingStrategy
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "EmbeddingStrategy",
    "EmbeddingRegistry",
    "embedding_registry",
    "EmbeddingType",
    "EmbeddingConfig",
    "BaseEmbeddingConfig",
    "SentenceTransformerEmbeddingConfig",
    "SentenceTransformerEmbeddingStrategy",
    "OpenAIEmbeddingConfig",
    "OpenAIEmbeddingStrategy",
    "OllamaEmbeddingConfig",
    "OllamaEmbeddingStrategy",
    "CohereEmbeddingConfig",
    "CohereEmbeddingStrategy",
    "VoyageEmbeddingConfig",
    "VoyageEmbeddingStrategy",
    "HuggingFaceEmbeddingConfig",
    "HuggingFaceEmbeddingStrategy",
    "MedCPTEmbeddingConfig",
]
