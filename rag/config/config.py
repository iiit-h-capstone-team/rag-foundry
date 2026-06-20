from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from .enums import (
    ChunkingType,
    EmbeddingType,
    RetrievalType,
    RerankerType,
    VectorStoreType,
    GenerationType,
    EvaluationType
)


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


@dataclass
class EmbeddingConfig:
    """Configuration for embedding strategies."""
    type: EmbeddingType
    model_name: Optional[str] = None
    model: Optional[str] = None
    dimension: int = 768
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorStoreConfig:
    """Configuration for vector store."""
    type: VectorStoreType
    dimension: int = 768
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalConfig:
    """Configuration for retrieval strategies."""
    type: RetrievalType
    top_k: int = 5
    initial_k: int = 20
    dense_weight: float = 0.7
    sparse_weight: float = 0.3
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RerankerConfig:
    """Configuration for reranking strategies."""
    type: RerankerType
    model_name: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationConfig:
    """Configuration for generation strategies."""
    type: GenerationType
    model: str
    max_tokens: int = 1024
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationConfig:
    """Configuration for evaluation strategies."""
    type: EvaluationType
    model: str = "llama-3.3-70b-versatile"
    max_tokens: int = 2000
    temperature: float = 0.0
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGConfig:
    """Complete RAG system configuration."""

    chunking: ChunkingConfig

    embedding: EmbeddingConfig

    vector_store: VectorStoreConfig

    retrieval: RetrievalConfig

    generation: GenerationConfig

    evaluation: EvaluationConfig

    reranker: Optional[RerankerConfig] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'chunking': self.chunking.__dict__,
            'embedding': self.embedding.__dict__,
            'vector_store': self.vector_store.__dict__,
            'retrieval': self.retrieval.__dict__,
            'reranker': self.reranker.__dict__ if self.reranker else None,
            'generation': self.generation.__dict__,
            'evaluation': self.evaluation.__dict__
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RAGConfig':
        """Create config from dictionary."""
        return cls(
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