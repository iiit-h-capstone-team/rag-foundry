"""Reranking module with registry-based strategy architecture."""

from rag.modules.reranking.base import RerankerStrategy
from rag.modules.reranking.registry import reranking_registry, RerankingRegistry
from rag.modules.reranking.enums import RerankingType
from rag.modules.reranking.config import RerankingConfig, BaseRerankingConfig

from rag.modules.reranking.strategies.cohere.config import CohereRerankingConfig
from rag.modules.reranking.strategies.cohere.strategy import CohereRerankingStrategy

from rag.modules.reranking.strategies.jina.config import JinaRerankingConfig
from rag.modules.reranking.strategies.jina.strategy import JinaRerankingStrategy

from rag.modules.reranking.strategies.cross_encoder.config import CrossEncoderRerankingConfig
try:
    from rag.modules.reranking.strategies.cross_encoder.strategy import CrossEncoderRerankingStrategy
except ImportError:
    pass

from rag.modules.reranking.strategies.mixedbread.config import MixedBreadRerankingConfig
from rag.modules.reranking.strategies.mixedbread.strategy import MixedBreadRerankingStrategy

from rag.modules.reranking.strategies.voyage.config import VoyageRerankingConfig
from rag.modules.reranking.strategies.voyage.strategy import VoyageRerankingStrategy


__all__ = [
    "RerankerStrategy",
    "RerankingRegistry",
    "reranking_registry",
    "RerankingType",
    "RerankingConfig",
    "BaseRerankingConfig",
    "CohereRerankingConfig",
    "CohereRerankingStrategy",
    "JinaRerankingConfig",
    "JinaRerankingStrategy",
    "CrossEncoderRerankingConfig",
    "CrossEncoderRerankingStrategy",
    "MixedBreadRerankingConfig",
    "MixedBreadRerankingStrategy",
    "VoyageRerankingConfig",
    "VoyageRerankingStrategy",
]
