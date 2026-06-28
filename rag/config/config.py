from __future__ import annotations

from dataclasses import dataclass, field, is_dataclass, asdict
from enum import Enum
from typing import Dict, Any, Optional

from .enums import (
    ChunkingType,
    EmbeddingType,
    QueryTransformType,
    SearchType,
    FusionType,
    RerankerType,
    VectorStoreType,
    GenerationType,
    EvaluationType,
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


@dataclass
class ProviderConfig:
    """
    Configuration for LLM providers.

    Credentials are resolved at provider-initialization time from the
    environment variable named by ``api_key_env`` (e.g. ``GROQ_API_KEY``,
    ``OPENAI_API_KEY``). Environment variable names are never hardcoded in the
    provider layer; each provider declares its own via this field.
    """

    type: ProviderType
    api_key_env: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.type = ProviderType(self.type)


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------
@dataclass
class SentenceChunkingConfig:
    """Tunables for the sentence chunking strategy."""
    max_words: int = 100
    overlap_sentences: int = 1


@dataclass
class FixedWindowChunkingConfig:
    """Tunables for the fixed-window chunking strategy."""
    window_size: int = 256
    overlap: int = 50


@dataclass
class TokenChunkingConfig:
    """Tunables for the token chunking strategy."""
    max_tokens: int = 200
    overlap_tokens: int = 20

@dataclass
class SemanticChunkingConfig:
    embedding: EmbeddingConfig
    max_words: int = 256
    similarity_threshold: float = 0.8
    overlap_sentences: int = 1
    similarity_window: int = 5

    def __post_init__(self):
        self.embedding = _coerce(self.embedding, EmbeddingConfig)


_CHUNKING_CONFIGS = {
    ChunkingType.SENTENCE: SentenceChunkingConfig,
    ChunkingType.FIXED_WINDOW: FixedWindowChunkingConfig,
    ChunkingType.TOKEN: TokenChunkingConfig,
    ChunkingType.SEMANTIC: SemanticChunkingConfig,
}


@dataclass
class ChunkingConfig:
    """Chunking section: which strategy plus its own typed config."""
    type: ChunkingType
    config: Any = None

    def __post_init__(self):
        self.type = ChunkingType(self.type)
        self.config = _coerce(self.config, _CHUNKING_CONFIGS[self.type])


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------
@dataclass
class SentenceTransformerEmbeddingConfig:
    """Tunables for the sentence-transformer embedding strategy."""
    model_name: Optional[str] = None
    model: Optional[str] = None
    dimension: int = 768


@dataclass
class OpenAIEmbeddingConfig:
    """Tunables for the OpenAI embedding strategy."""
    model: Optional[str] = None
    model_name: Optional[str] = None
    dimension: int = 1536


@dataclass
class OllamaEmbeddingConfig:
    """Tunables for the Ollama embedding strategy."""
    model_name: Optional[str] = None
    model: Optional[str] = None
    dimension: int = 768
    base_url: str = "http://localhost:11434"


@dataclass
class CohereEmbeddingConfig:
    """Tunables for the Cohere embedding strategy."""
    model_name: Optional[str] = None
    model: Optional[str] = None
    dimension: int = 1024
    input_type: str = "search_document"


@dataclass
class VoyageEmbeddingConfig:
    """Tunables for the Voyage AI embedding strategy."""
    model_name: Optional[str] = None
    model: Optional[str] = None
    dimension: int = 1024
    input_type: Optional[str] = None


@dataclass
class HuggingFaceEmbeddingConfig:
    """Tunables for the HuggingFace Inference embedding strategy."""
    model_name: Optional[str] = None
    model: Optional[str] = None
    dimension: int = 768
    api_url: Optional[str] = None


@dataclass
class MedCPTEmbeddingConfig:
    """Tunables for the MedCPT embedding strategy (dual encoder)."""
    query_model_name: str = "ncbi/MedCPT-Query-Encoder"
    article_model_name: str = "ncbi/MedCPT-Article-Encoder"
    dimension: int = 768


_EMBEDDING_CONFIGS = {
    EmbeddingType.SENTENCE_TRANSFORMER: SentenceTransformerEmbeddingConfig,
    EmbeddingType.OPENAI: OpenAIEmbeddingConfig,
    EmbeddingType.OLLAMA: OllamaEmbeddingConfig,
    EmbeddingType.COHERE: CohereEmbeddingConfig,
    EmbeddingType.VOYAGE: VoyageEmbeddingConfig,
    EmbeddingType.HUGGINGFACE: HuggingFaceEmbeddingConfig,
    EmbeddingType.MEDCPT: MedCPTEmbeddingConfig,
}


@dataclass
class EmbeddingConfig:
    """Embedding section: which strategy plus its own typed config."""
    type: EmbeddingType
    config: Any = None

    def __post_init__(self):
        self.type = EmbeddingType(self.type)
        self.config = _coerce(self.config, _EMBEDDING_CONFIGS[self.type])


# ---------------------------------------------------------------------------
# Vector store
# ---------------------------------------------------------------------------
@dataclass
class FaissVectorStoreConfig:
    """Tunables for the FAISS vector store."""
    dimension: int = 768


_VECTORSTORE_CONFIGS = {
    VectorStoreType.FAISS: FaissVectorStoreConfig,
}


@dataclass
class VectorStoreConfig:
    """Vector store section: which store plus its own typed config."""
    type: VectorStoreType
    config: Any = None

    def __post_init__(self):
        self.type = VectorStoreType(self.type)
        self.config = _coerce(self.config, _VECTORSTORE_CONFIGS[self.type])


# ---------------------------------------------------------------------------
# Retrieval pipeline
# ---------------------------------------------------------------------------
@dataclass
class NoOpQueryTransformConfig:
    """No-op query transform; passes the query through unchanged."""


@dataclass
class DenseSearchConfig:
    """Tunables for dense vector search."""
    top_k: int = 5


@dataclass
class SparseSearchConfig:
    """Tunables for sparse (BM25) search."""
    top_k: int = 5


@dataclass
class NoOpFusionConfig:
    """No-op fusion; passes a single search list through unchanged."""


@dataclass
class RRFFusionConfig:
    """Tunables for reciprocal rank fusion."""
    top_k: int = 5
    k: int = 60


@dataclass
class WeightedSumFusionConfig:
    """Tunables for weighted score fusion across search lists."""
    top_k: int = 5
    weights: list = field(default_factory=list)


_QUERY_TRANSFORM_CONFIGS = {
    QueryTransformType.NOOP: NoOpQueryTransformConfig,
}

_SEARCH_CONFIGS = {
    SearchType.DENSE: DenseSearchConfig,
    SearchType.SPARSE: SparseSearchConfig,
}

_FUSION_CONFIGS = {
    FusionType.NOOP: NoOpFusionConfig,
    FusionType.RRF: RRFFusionConfig,
    FusionType.WEIGHTED_SUM: WeightedSumFusionConfig,
}


@dataclass
class QueryTransformConfig:
    """Query-transform stage inside the retrieval pipeline."""
    type: QueryTransformType
    config: Any = None

    def __post_init__(self):
        self.type = QueryTransformType(self.type)
        self.config = _coerce(self.config, _QUERY_TRANSFORM_CONFIGS[self.type])


@dataclass
class SearchStrategyConfig:
    """One search strategy entry inside the search sub-pipeline."""
    type: SearchType
    config: Any = None

    def __post_init__(self):
        self.type = SearchType(self.type)
        self.config = _coerce(self.config, _SEARCH_CONFIGS[self.type])


@dataclass
class SearchPipelineConfig:
    """Search sub-pipeline: one or more search strategies (mandatory)."""
    searches: list

    def __post_init__(self):
        if not self.searches:
            raise ValueError("retrieval.search.searches must contain at least one search")
        self.searches = [
            item if isinstance(item, SearchStrategyConfig) else SearchStrategyConfig(**item)
            for item in self.searches
        ]


@dataclass
class FusionConfig:
    """Fusion stage inside the retrieval pipeline."""
    type: FusionType
    config: Any = None

    def __post_init__(self):
        self.type = FusionType(self.type)
        self.config = _coerce(self.config, _FUSION_CONFIGS[self.type])


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
@dataclass
class CrossEncoderRerankerConfig:
    """Tunables for the cross-encoder reranker."""
    model_name: Optional[str] = None
    top_k: int = 5


@dataclass
class CohereRerankerConfig:
    """Tunables for the Cohere reranker."""
    model_name: Optional[str] = None
    model: Optional[str] = None
    top_n: int = 10


@dataclass
class VoyageRerankerConfig:
    """Tunables for the Voyage AI reranker."""
    model_name: Optional[str] = None
    model: Optional[str] = None
    top_k: int = 10


@dataclass
class JinaRerankerConfig:
    """Tunables for the Jina AI reranker."""
    model_name: Optional[str] = None
    model: Optional[str] = None
    top_n: int = 10


@dataclass
class MixedBreadRerankerConfig:
    """Tunables for the MixedBread AI reranker."""
    model_name: Optional[str] = None
    model: Optional[str] = None
    top_n: int = 10


_RERANKER_CONFIGS = {
    RerankerType.CROSS_ENCODER: CrossEncoderRerankerConfig,
    RerankerType.COHERE: CohereRerankerConfig,
    RerankerType.VOYAGE: VoyageRerankerConfig,
    RerankerType.JINA: JinaRerankerConfig,
    RerankerType.MIXEDBREAD: MixedBreadRerankerConfig,
}


@dataclass
class RerankerConfig:
    """Reranker section: which strategy plus its own typed config."""
    type: RerankerType
    config: Any = None

    def __post_init__(self):
        self.type = RerankerType(self.type)
        self.config = _coerce(self.config, _RERANKER_CONFIGS[self.type])


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
@dataclass
class DefaultGenerationConfig:
    """Tunables for the default generation strategy."""
    model: str
    max_tokens: int = 1024
    temperature: float = 0.7
    system_prompt: Optional[str] = None


_GENERATION_CONFIGS = {
    GenerationType.DEFAULT: DefaultGenerationConfig,
}


@dataclass
class GenerationConfig:
    """Generation section: strategy + provider dependency + typed config."""
    strategy: GenerationType
    provider: str
    config: Any = None

    def __post_init__(self):
        self.strategy = GenerationType(self.strategy)
        self.config = _coerce(self.config, _GENERATION_CONFIGS[self.strategy])


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
@dataclass
class TRACeEvaluationConfig:
    """Tunables for the TRACe evaluation strategy."""
    model: str = "llama-3.3-70b-versatile"
    max_tokens: int = 2000
    temperature: float = 0.0


_EVALUATION_CONFIGS = {
    EvaluationType.TRACE: TRACeEvaluationConfig,
}


@dataclass
class EvaluationConfig:
    """Evaluation section: strategy + provider dependency + typed config."""
    type: EvaluationType
    provider: str
    config: Any = None

    def __post_init__(self):
        self.type = EvaluationType(self.type)
        self.config = _coerce(self.config, _EVALUATION_CONFIGS[self.type])


@dataclass
class CacheConfig:
    """Cache subsystem settings.

    Caching is content-addressed and never auto-deletes entries; toggling
    ``enabled`` off bypasses the cache entirely.
    """
    enabled: bool = True
    cache_dir: str = "./cache"


@dataclass
class RAGConfig:
    """Complete RAG system configuration."""

    providers: Dict[str, ProviderConfig]

    chunking: ChunkingConfig

    embedding: EmbeddingConfig

    vector_store: VectorStoreConfig

    retrieval: RetrievalConfig

    generation: GenerationConfig

    evaluation: EvaluationConfig

    mode: Mode = Mode.DEV

    name: str = "default"

    cache: CacheConfig = field(default_factory=CacheConfig)

    def __post_init__(self):
        self.mode = Mode(self.mode)
        self.cache = _coerce(self.cache, CacheConfig)

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
            'evaluation': self._section_to_dict(self.evaluation),
            'cache': self._section_to_dict(self.cache)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RAGConfig':
        """Create config from dictionary."""
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
            evaluation=EvaluationConfig(**data.get('evaluation', {})),
            cache=CacheConfig(**data['cache']) if data.get('cache') else CacheConfig()
        )

    def model_dump(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return self.to_dict()

