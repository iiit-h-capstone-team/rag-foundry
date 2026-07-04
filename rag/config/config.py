from __future__ import annotations

from dataclasses import dataclass, field, is_dataclass, asdict
from enum import Enum
from typing import Dict, Any, Optional

from .enums import (
    ProviderType,
    Mode
)


def _coerce(value: Any, config_cls: type) -> Any:
    """Resolve a nested strategy config into its typed dataclass.

    Accepts ``None`` (use defaults), a plain dict (from JSON/YAML), or an
    already-built config object.
    """
    if value is None:
        return config_cls()
    if isinstance(value, dict):
        return config_cls(**value)
    return value


def _serialize_value(value: Any) -> Any:
    """Recursively serialize config values for dict/YAML export."""
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            key: _serialize_value(item)
            for key, item in asdict(value).items()
        }
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_value(item) for key, item in value.items()}
    return value


from providers.config import ProviderConfig




# ---------------------------------------------------------------------------
# Vector store
# ---------------------------------------------------------------------------
from vectorstore.config import VectorStoreConfig


# ---------------------------------------------------------------------------
# Retrieval pipeline
# ---------------------------------------------------------------------------
from rag.modules.query_transform.config import QueryTransformConfig
from rag.modules.search.config import SearchStrategyConfig, SearchPipelineConfig
from rag.modules.fusion.config import FusionConfig


@dataclass
class RetrievalConfig:
    """Retrieval pipeline: composable query transform, search, fusion, rerank."""
    search: SearchPipelineConfig
    query_transform: Optional[QueryTransformConfig] = None
    fusion: Optional[FusionConfig] = None
    rerank: Optional["RerankerConfig"] = None

    def __post_init__(self):
        if isinstance(self.search, dict):
            self.search = SearchPipelineConfig(**self.search)
        if isinstance(self.query_transform, dict):
            self.query_transform = QueryTransformConfig(**self.query_transform)
        if isinstance(self.fusion, dict):
            self.fusion = FusionConfig(**self.fusion)
        if isinstance(self.rerank, dict):
            self.rerank = RerankerConfig(**self.rerank)
        if len(self.search.searches) > 1 and self.fusion is None:
            raise ValueError(
                "retrieval.fusion is required when search.searches "
                "contains more than one strategy"
            )


# ---------------------------------------------------------------------------
# Reranker
# ---------------------------------------------------------------------------
from rag.modules.reranking.config import RerankingConfig as RerankerConfig
from rag.modules.reranking.strategies.cross_encoder.config import CrossEncoderRerankingConfig as CrossEncoderRerankerConfig
from rag.modules.reranking.strategies.cohere.config import CohereRerankingConfig as CohereRerankerConfig
from rag.modules.reranking.strategies.voyage.config import VoyageRerankingConfig as VoyageRerankerConfig
from rag.modules.reranking.strategies.jina.config import JinaRerankingConfig as JinaRerankerConfig
from rag.modules.reranking.strategies.mixedbread.config import MixedBreadRerankingConfig as MixedBreadRerankerConfig


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
from rag.modules.generation.config import GenerationConfig
from rag.modules.generation.strategies.default.config import DefaultGenerationConfig


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
from evaluation.config import EvaluationConfig
from evaluation.strategies.trace.config import TRACeEvaluationConfig


@dataclass
class CacheConfig:
    """Cache subsystem settings.

    Caching is content-addressed and never auto-deletes entries; toggling
    ``enabled`` off bypasses the cache entirely.
    """
    enabled: bool = True
    cache_dir: str = "./cache"


@dataclass
class LoggingConfig:
    """Logging configuration for experiment execution."""
    enabled: bool = True
    level: str = "INFO"
    show_progress: bool = True


@dataclass
class RAGConfig:
    """Complete RAG system configuration."""

    providers: Dict[str, ProviderConfig]

    chunking: ChunkingConfig

    embedding: EmbeddingConfig

    vector_store: VectorStoreConfig

    retrieval: RetrievalConfig

    generation: GenerationConfig

    evaluation: Optional[EvaluationConfig] = None

    mode: Mode = Mode.DEV

    name: str = "default"

    cache: CacheConfig = field(default_factory=CacheConfig)

    # Query range override (takes precedence over experiment config)
    start_index: int | None = None
    end_index: int | None = None

    # Logging configuration
    logging_config: LoggingConfig = field(default_factory=LoggingConfig)

    def __post_init__(self):
        self.mode = Mode(self.mode)
        self.cache = _coerce(self.cache, CacheConfig)
        self.logging_config = _coerce(self.logging_config, LoggingConfig)

    @staticmethod
    def _section_to_dict(section) -> Dict[str, Any]:
        """Serialize a config section, converting enums and nested configs."""
        result: Dict[str, Any] = {}
        for key, value in section.__dict__.items():
            result[key] = _serialize_value(value)
        return result

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'name': self.name,
            'mode': self.mode.value,
            'providers': {
                name: self._section_to_dict(provider)
                for name, provider in self.providers.items()
            },
            'chunking': self._section_to_dict(self.chunking),
            'embedding': self._section_to_dict(self.embedding),
            'vector_store': self._section_to_dict(self.vector_store),
            'retrieval': self._section_to_dict(self.retrieval),
            'generation': self._section_to_dict(self.generation),
            'evaluation': self._section_to_dict(self.evaluation) if self.evaluation else None,
            'cache': self._section_to_dict(self.cache),
            'start_index': self.start_index,
            'end_index': self.end_index,
            'logging_config': self._section_to_dict(self.logging_config)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RAGConfig':
        """Create config from dictionary."""
        from rag.modules.chunking.config import ChunkingConfig
        from embedding.config import EmbeddingConfig
        return cls(
            name=data.get('name', 'default'),
            mode=data.get('mode', Mode.DEV),
            providers={
                name: ProviderConfig(**provider_data)
                for name, provider_data in data.get('providers', {}).items()
            },
            chunking=ChunkingConfig(**data.get('chunking', {})),
            embedding=EmbeddingConfig(**data.get('embedding', {})),
            vector_store=VectorStoreConfig(**data.get('vector_store', {})),
            retrieval=RetrievalConfig(**data.get('retrieval', {})),
            generation=GenerationConfig(**data.get('generation', {})),
            evaluation=EvaluationConfig(**data['evaluation']) if data.get('evaluation') else None,
            cache=CacheConfig(**data['cache']) if data.get('cache') else CacheConfig(),
            start_index=data.get('start_index'),
            end_index=data.get('end_index'),
            logging_config=LoggingConfig(**data.get('logging_config', {})) if data.get('logging_config') else LoggingConfig()
        )

    def model_dump(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return self.to_dict()

