from dataclasses import dataclass, field, is_dataclass, asdict
from enum import Enum
from typing import Dict, Any, Optional

from .enums import (
    ChunkingType,
    EmbeddingType,
    RetrievalType,
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


_CHUNKING_CONFIGS = {
    ChunkingType.SENTENCE: SentenceChunkingConfig,
    ChunkingType.FIXED_WINDOW: FixedWindowChunkingConfig,
    ChunkingType.TOKEN: TokenChunkingConfig,
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


_EMBEDDING_CONFIGS = {
    EmbeddingType.SENTENCE_TRANSFORMER: SentenceTransformerEmbeddingConfig,
    EmbeddingType.OPENAI: OpenAIEmbeddingConfig,
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
# Retrieval
# ---------------------------------------------------------------------------
@dataclass
class DenseRetrievalConfig:
    """Tunables for dense retrieval."""
    top_k: int = 5


@dataclass
class DenseRerankRetrievalConfig:
    """Tunables for dense retrieval followed by reranking."""
    top_k: int = 5
    initial_k: int = 20


@dataclass
class HybridRetrievalConfig:
    """Tunables for hybrid (dense + sparse) retrieval."""
    top_k: int = 5
    initial_k: int = 20
    dense_weight: float = 0.7
    sparse_weight: float = 0.3


_RETRIEVAL_CONFIGS = {
    RetrievalType.DENSE: DenseRetrievalConfig,
    RetrievalType.DENSE_RERANK: DenseRerankRetrievalConfig,
    RetrievalType.HYBRID: HybridRetrievalConfig,
}


@dataclass
class RetrievalConfig:
    """Retrieval section: which strategy plus its own typed config."""
    type: RetrievalType
    config: Any = None

    def __post_init__(self):
        self.type = RetrievalType(self.type)
        self.config = _coerce(self.config, _RETRIEVAL_CONFIGS[self.type])


# ---------------------------------------------------------------------------
# Reranker
# ---------------------------------------------------------------------------
@dataclass
class CrossEncoderRerankerConfig:
    """Tunables for the cross-encoder reranker."""
    model_name: Optional[str] = None


_RERANKER_CONFIGS = {
    RerankerType.CROSS_ENCODER: CrossEncoderRerankerConfig,
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
class RAGConfig:
    """Complete RAG system configuration."""

    providers: Dict[str, ProviderConfig]

    chunking: ChunkingConfig

    embedding: EmbeddingConfig

    vector_store: VectorStoreConfig

    retrieval: RetrievalConfig

    generation: GenerationConfig

    evaluation: EvaluationConfig

    reranker: Optional[RerankerConfig] = None

    mode: Mode = Mode.DEV

    def __post_init__(self):
        self.mode = Mode(self.mode)

    @staticmethod
    def _section_to_dict(section) -> Dict[str, Any]:
        """Serialize a config section, converting enums and nested configs."""
        result: Dict[str, Any] = {}
        for key, value in section.__dict__.items():
            if isinstance(value, Enum):
                result[key] = value.value
            elif is_dataclass(value) and not isinstance(value, type):
                result[key] = asdict(value)
            else:
                result[key] = value
        return result

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'mode': self.mode.value,
            'providers': {
                name: self._section_to_dict(provider)
                for name, provider in self.providers.items()
            },
            'chunking': self._section_to_dict(self.chunking),
            'embedding': self._section_to_dict(self.embedding),
            'vector_store': self._section_to_dict(self.vector_store),
            'retrieval': self._section_to_dict(self.retrieval),
            'reranker': (
                self._section_to_dict(self.reranker)
                if self.reranker else None
            ),
            'generation': self._section_to_dict(self.generation),
            'evaluation': self._section_to_dict(self.evaluation)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RAGConfig':
        """Create config from dictionary."""
        return cls(
            mode=data.get('mode', Mode.DEV),
            providers={
                name: ProviderConfig(**provider_data)
                for name, provider_data in data.get('providers', {}).items()
            },
            chunking=ChunkingConfig(**data.get('chunking', {})),
            embedding=EmbeddingConfig(**data.get('embedding', {})),
            vector_store=VectorStoreConfig(**data.get('vector_store', {})),
            retrieval=RetrievalConfig(**data.get('retrieval', {})),
            reranker=(
                RerankerConfig(**data['reranker'])
                if data.get('reranker') else None
            ),
            generation=GenerationConfig(**data.get('generation', {})),
            evaluation=EvaluationConfig(**data.get('evaluation', {}))
        )
