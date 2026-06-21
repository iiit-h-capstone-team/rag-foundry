from dataclasses import dataclass, field
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
    ProviderType
)

@dataclass
class ProviderConfig:
    """
    Configuration for LLM providers.
    """

    type: ProviderType
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkingConfig:
    """Configuration for chunking strategies."""
    type: ChunkingType
    max_words: int = 100
    overlap_sentences: int = 1
    window_size: int = 256
    overlap: int = 50
    max_tokens: int = 200
    overlap_tokens: int = 20
    params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.type = ChunkingType(self.type)


@dataclass
class EmbeddingConfig:
    """Configuration for embedding strategies."""
    type: EmbeddingType
    model_name: Optional[str] = None
    model: Optional[str] = None
    dimension: int = 768
    params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.type = EmbeddingType(self.type)


@dataclass
class VectorStoreConfig:
    """Configuration for vector store."""
    type: VectorStoreType
    dimension: int = 768
    params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.type = VectorStoreType(self.type)


@dataclass
class RetrievalConfig:
    """Configuration for retrieval strategies."""
    type: RetrievalType
    top_k: int = 5
    initial_k: int = 20
    dense_weight: float = 0.7
    sparse_weight: float = 0.3
    params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.type = RetrievalType(self.type)


@dataclass
class RerankerConfig:
    """Configuration for reranking strategies."""
    type: RerankerType
    model_name: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.type = RerankerType(self.type)


@dataclass
class GenerationConfig:
    """
    Configuration for generation strategies.
    """

    strategy: GenerationType
    provider: str
    model: str
    max_tokens: int = 1024
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    def __post_init__(self):
        self.strategy = GenerationType(
            self.strategy
        )


@dataclass
class EvaluationConfig:
    """
    Configuration for evaluation strategies.
    """
    type: EvaluationType
    provider: str
    model: str = "llama-3.3-70b-versatile"
    max_tokens: int = 2000
    temperature: float = 0.0
    params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.type = EvaluationType(self.type)


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

    @staticmethod
    def _section_to_dict(section) -> Dict[str, Any]:
        """Serialize a config section, converting enum fields to their values."""
        return {
            key: (value.value if isinstance(value, Enum) else value)
            for key, value in section.__dict__.items()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
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