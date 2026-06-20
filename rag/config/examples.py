"""
Example RAG configurations for different use cases.
"""

from rag.config.config import (
    RAGConfig,
    ChunkingConfig,
    EmbeddingConfig,
    VectorStoreConfig,
    RetrievalConfig,
    GenerationConfig,
    EvaluationConfig
)
from rag.config.enums import (
    ChunkingType,
    EmbeddingType,
    VectorStoreType,
    RetrievalType,
    GenerationType,
    EvaluationType
)


# Configuration 1: Fast & Local (No API Calls)
config_fast_local = RAGConfig(
    chunking=ChunkingConfig(
        type=ChunkingType.FIXED_WINDOW,
        window_size=256,
        overlap=50
    ),
    embedding=EmbeddingConfig(
        type=EmbeddingType.LOCAL,
        model_name='sentence-transformers/all-MiniLM-L6-v2',
        dimension=384
    ),
    vector_store=VectorStoreConfig(
        type=VectorStoreType.FAISS,
        dimension=384
    ),
    retrieval=RetrievalConfig(
        type=RetrievalType.DENSE,
        top_k=5,
        initial_k=10
    ),
    generation=GenerationConfig(
        type=GenerationType.GROQ,
        model='llama-3.1-8b-instant',
        max_tokens=512,
        temperature=0.5
    ),
    evaluation=EvaluationConfig(
        type=EvaluationType.TRACE,
        model='llama-3.1-8b-instant'
    )
)


# Configuration 2: High Quality with Reranking
config_high_quality = RAGConfig(
    chunking=ChunkingConfig(
        type=ChunkingType.SENTENCE,
        max_words=100,
        overlap_sentences=1
    ),
    embedding=EmbeddingConfig(
        type=EmbeddingType.BGE,
        model_name='BAAI/bge-large-en-v1.5',
        dimension=1024
    ),
    vector_store=VectorStoreConfig(
        type=VectorStoreType.FAISS,
        dimension=1024
    ),
    retrieval=RetrievalConfig(
        type=RetrievalType.DENSE_RERANK,
        top_k=5,
        initial_k=20
    ),
    generation=GenerationConfig(
        type=GenerationType.GROQ,
        model='llama-3.3-70b-versatile',
        max_tokens=1024,
        temperature=0.7
    ),
    evaluation=EvaluationConfig(
        type=EvaluationType.TRACE,
        model='llama-3.3-70b-versatile'
    )
)


# Configuration 3: OpenAI-based (Production Grade)
config_openai_production = RAGConfig(
    chunking=ChunkingConfig(
        type=ChunkingType.TOKEN,
        max_tokens=200,
        overlap_tokens=20
    ),
    embedding=EmbeddingConfig(
        type=EmbeddingType.OPENAI,
        model='text-embedding-3-large',
        dimension=3072
    ),
    vector_store=VectorStoreConfig(
        type=VectorStoreType.FAISS,
        dimension=3072
    ),
    retrieval=RetrievalConfig(
        type=RetrievalType.HYBRID,
        top_k=5,
        initial_k=25,
        dense_weight=0.7,
        sparse_weight=0.3
    ),
    generation=GenerationConfig(
        type=GenerationType.OPENAI,
        model='gpt-4',
        max_tokens=2048,
        temperature=0.3,
        system_prompt='You are a helpful assistant that answers questions based on provided context.'
    ),
    evaluation=EvaluationConfig(
        type=EvaluationType.TRACE,
        model='gpt-4'
    )
)


# Configuration 4: Medical/Scientific Documents
config_medical = RAGConfig(
    chunking=ChunkingConfig(
        type=ChunkingType.SENTENCE,
        max_words=150,
        overlap_sentences=2
    ),
    embedding=EmbeddingConfig(
        type=EmbeddingType.BGE,
        model_name='pritamdeka/S-PubMedBert-MS-MARCO',
        dimension=768
    ),
    vector_store=VectorStoreConfig(
        type=VectorStoreType.FAISS,
        dimension=768
    ),
    retrieval=RetrievalConfig(
        type=RetrievalType.DENSE_RERANK,
        top_k=10,
        initial_k=30
    ),
    generation=GenerationConfig(
        type=GenerationType.GROQ,
        model='llama-3.3-70b-versatile',
        max_tokens=1024,
        temperature=0.2
    ),
    evaluation=EvaluationConfig(
        type=EvaluationType.TRACE,
        model='llama-3.3-70b-versatile'
    )
)


# Configuration 5: Cost-Optimized
config_cost_optimized = RAGConfig(
    chunking=ChunkingConfig(
        type=ChunkingType.FIXED_WINDOW,
        window_size=512,
        overlap=100
    ),
    embedding=EmbeddingConfig(
        type=EmbeddingType.LOCAL,
        model_name='sentence-transformers/all-mpnet-base-v2',
        dimension=768
    ),
    vector_store=VectorStoreConfig(
        type=VectorStoreType.FAISS,
        dimension=768
    ),
    retrieval=RetrievalConfig(
        type=RetrievalType.DENSE,
        top_k=3,
        initial_k=10
    ),
    generation=GenerationConfig(
        type=GenerationType.GROQ,
        model='llama-3.1-8b-instant',
        max_tokens=256,
        temperature=0.5
    ),
    evaluation=EvaluationConfig(
        type=EvaluationType.TRACE,
        model='llama-3.1-8b-instant'
    )
)


def get_default_config() -> RAGConfig:
    """Get default configuration."""
    return config_fast_local


def get_config_by_name(name: str) -> RAGConfig:
    """Get configuration by name."""
    configs = {
        'fast_local': config_fast_local,
        'high_quality': config_high_quality,
        'openai_production': config_openai_production,
        'medical': config_medical,
        'cost_optimized': config_cost_optimized
    }
    return configs.get(name, config_fast_local)


if __name__ == "__main__":
    print("Available Configurations:")
    print("1. fast_local - Fast & local (no API calls)")
    print("2. high_quality - High quality with reranking")
    print("3. openai_production - Production grade OpenAI")
    print("4. medical - Medical/scientific documents")
    print("5. cost_optimized - Cost optimized")

    config = get_config_by_name('high_quality')
    print(f"\nSelected: high_quality")
    print(f"Chunking: {config.chunking.type}")
    print(f"Embedding: {config.embedding.type}")
    print(f"Retrieval: {config.retrieval.type}")
    print(f"Generation: {config.generation.type}")
    print(f"Evaluation: {config.evaluation.type}")
