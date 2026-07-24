"""
Example RAG configurations for different use cases.

Every configuration is self-contained: each strategy section names the
strategy and nests its own typed config object (e.g. ``SentenceChunkingConfig``),
and providers declare their own credential environment variable via
``api_key_env`` (resolved at pipeline-build time).
"""

from rag.config.config import (
    RAGConfig,
    ProviderConfig,
    VectorStoreConfig,
    RetrievalConfig,
)
from vectorstore import FaissVectorStoreConfig
from rag.modules.search import SearchPipelineConfig, SearchStrategyConfig, DenseSearchConfig, SparseSearchConfig
from rag.modules.fusion import FusionConfig, WeightedSumFusionConfig
from rag.modules.reranking import RerankerConfig, CrossEncoderRerankerConfig
from rag.modules.generation import GenerationConfig, DefaultGenerationConfig
from evaluation import EvaluationConfig, TRACeEvaluationConfig
from rag.modules.chunking import (
    ChunkingConfig,
    SentenceChunkingConfig,
    FixedWindowChunkingConfig,
    FixedWordChunkingConfig,
    TokenChunkingConfig,
    ChunkingType,
)
from embedding import (
    EmbeddingConfig,
    SentenceTransformerEmbeddingConfig,
    OpenAIEmbeddingConfig,
    EmbeddingType,
)
from rag.config.enums import (
    ProviderType,
    VectorStoreType,
    SearchType,
    FusionType,
    RerankerType,
    GenerationType,
    EvaluationType
)


def _groq_provider() -> dict:
    """A single Groq provider reading credentials from ``GROQ_API_KEY``."""
    return {
        "groq": ProviderConfig(
            type=ProviderType.GROQ,
            api_key_env="GROQ_API_KEY",
            params={"cooldown_seconds": 60}
        )
    }


def _dense_search(top_k: int = 5) -> RetrievalConfig:
    return RetrievalConfig(
        search=SearchPipelineConfig(
            searches=[
                SearchStrategyConfig(
                    type=SearchType.DENSE,
                    config=DenseSearchConfig(top_k=top_k),
                )
            ]
        )
    )


# Configuration 1: Fast & Local embeddings, Groq generation/evaluation
config_fast_local = RAGConfig(
    providers=_groq_provider(),
    chunking=ChunkingConfig(
        type=ChunkingType.FIXED_WINDOW,
        config=FixedWindowChunkingConfig(
            window_size=256,
            overlap=50
        )
    ),
    embedding=EmbeddingConfig(
        type=EmbeddingType.SENTENCE_TRANSFORMER,
        config=SentenceTransformerEmbeddingConfig(
            model_name='sentence-transformers/all-MiniLM-L6-v2',
            dimension=384
        )
    ),
    vector_store=VectorStoreConfig(
        type=VectorStoreType.FAISS,
        config=FaissVectorStoreConfig(dimension=384)
    ),
    retrieval=_dense_search(top_k=5),
    generation=GenerationConfig(
        strategy=GenerationType.DEFAULT,
        provider='groq',
        config=DefaultGenerationConfig(
            model='llama-3.1-8b-instant',
            max_tokens=512,
            temperature=0.5
        )
    ),
    evaluation=EvaluationConfig(
        type=EvaluationType.TRACE,
        provider='groq',
        config=TRACeEvaluationConfig(model='llama-3.1-8b-instant')
    )
)


# Configuration 2: High Quality with Reranking
config_high_quality = RAGConfig(
    providers=_groq_provider(),
    chunking=ChunkingConfig(
        type=ChunkingType.SENTENCE,
        config=SentenceChunkingConfig(
            max_words=100,
            overlap_sentences=1
        )
    ),
    embedding=EmbeddingConfig(
        type=EmbeddingType.SENTENCE_TRANSFORMER,
        config=SentenceTransformerEmbeddingConfig(
            model_name='BAAI/bge-large-en-v1.5',
            dimension=1024
        )
    ),
    vector_store=VectorStoreConfig(
        type=VectorStoreType.FAISS,
        config=FaissVectorStoreConfig(dimension=1024)
    ),
    retrieval=RetrievalConfig(
        search=SearchPipelineConfig(
            searches=[
                SearchStrategyConfig(
                    type=SearchType.DENSE,
                    config=DenseSearchConfig(top_k=20),
                )
            ]
        ),
        rerank=RerankerConfig(
            type=RerankerType.CROSS_ENCODER,
            config=CrossEncoderRerankerConfig(
                model_name='BAAI/bge-reranker-v2-m3',
                top_k=5,
            )
        ),
    ),
    generation=GenerationConfig(
        strategy=GenerationType.DEFAULT,
        provider='groq',
        config=DefaultGenerationConfig(
            model='llama-3.3-70b-versatile',
            max_tokens=1024,
            temperature=0.7
        )
    ),
    evaluation=EvaluationConfig(
        type=EvaluationType.TRACE,
        provider='groq',
        config=TRACeEvaluationConfig(model='llama-3.3-70b-versatile')
    )
)


# Configuration 3: OpenAI-based (Production Grade).
# Demonstrates provider-specific env resolution: OpenAI for generation,
# Groq for evaluation, each reading its own api_key_env.
config_openai_production = RAGConfig(
    providers={
        "openai": ProviderConfig(
            type=ProviderType.OPENAI,
            api_key_env="OPENAI_API_KEY"
        ),
        "groq": ProviderConfig(
            type=ProviderType.GROQ,
            api_key_env="GROQ_API_KEY"
        ),
    },
    chunking=ChunkingConfig(
        type=ChunkingType.FIXED_WORD,
        config=FixedWordChunkingConfig(
            max_words=200,
            overlap_words=20
        )
    ),
    embedding=EmbeddingConfig(
        type=EmbeddingType.OPENAI,
        config=OpenAIEmbeddingConfig(
            model='text-embedding-3-large',
            dimension=3072
        )
    ),
    vector_store=VectorStoreConfig(
        type=VectorStoreType.FAISS,
        config=FaissVectorStoreConfig(dimension=3072)
    ),
    retrieval=RetrievalConfig(
        search=SearchPipelineConfig(
            searches=[
                SearchStrategyConfig(
                    type=SearchType.DENSE,
                    config=DenseSearchConfig(top_k=40),
                ),
                SearchStrategyConfig(
                    type=SearchType.SPARSE,
                    config=SparseSearchConfig(top_k=40),
                ),
            ]
        ),
        fusion=FusionConfig(
            type=FusionType.WEIGHTED_SUM,
            config=WeightedSumFusionConfig(
                top_k=5,
                weights=[0.7, 0.3],
            ),
        ),
    ),
    generation=GenerationConfig(
        strategy=GenerationType.DEFAULT,
        provider='openai',
        config=DefaultGenerationConfig(
            model='gpt-4',
            max_tokens=2048,
            temperature=0.3,
            system_prompt='You are a helpful assistant that answers questions based on provided context.'
        )
    ),
    evaluation=EvaluationConfig(
        type=EvaluationType.TRACE,
        provider='groq',
        config=TRACeEvaluationConfig(model='llama-3.3-70b-versatile')
    )
)


# Configuration 4: Medical/Scientific Documents
config_medical = RAGConfig(
    providers=_groq_provider(),
    chunking=ChunkingConfig(
        type=ChunkingType.SENTENCE,
        config=SentenceChunkingConfig(
            max_words=150,
            overlap_sentences=2
        )
    ),
    embedding=EmbeddingConfig(
        type=EmbeddingType.SENTENCE_TRANSFORMER,
        config=SentenceTransformerEmbeddingConfig(
            model_name='pritamdeka/S-PubMedBert-MS-MARCO',
            dimension=768
        )
    ),
    vector_store=VectorStoreConfig(
        type=VectorStoreType.FAISS,
        config=FaissVectorStoreConfig(dimension=768)
    ),
    retrieval=RetrievalConfig(
        search=SearchPipelineConfig(
            searches=[
                SearchStrategyConfig(
                    type=SearchType.DENSE,
                    config=DenseSearchConfig(top_k=30),
                )
            ]
        ),
        rerank=RerankerConfig(
            type=RerankerType.CROSS_ENCODER,
            config=CrossEncoderRerankerConfig(
                model_name='BAAI/bge-reranker-v2-m3',
                top_k=10,
            )
        ),
    ),
    generation=GenerationConfig(
        strategy=GenerationType.DEFAULT,
        provider='groq',
        config=DefaultGenerationConfig(
            model='llama-3.3-70b-versatile',
            max_tokens=1024,
            temperature=0.2
        )
    ),
    evaluation=EvaluationConfig(
        type=EvaluationType.TRACE,
        provider='groq',
        config=TRACeEvaluationConfig(model='llama-3.3-70b-versatile')
    )
)


# Configuration 5: Cost-Optimized
config_cost_optimized = RAGConfig(
    providers=_groq_provider(),
    chunking=ChunkingConfig(
        type=ChunkingType.FIXED_WINDOW,
        config=FixedWindowChunkingConfig(
            window_size=512,
            overlap=100
        )
    ),
    embedding=EmbeddingConfig(
        type=EmbeddingType.SENTENCE_TRANSFORMER,
        config=SentenceTransformerEmbeddingConfig(
            model_name='sentence-transformers/all-mpnet-base-v2',
            dimension=768
        )
    ),
    vector_store=VectorStoreConfig(
        type=VectorStoreType.FAISS,
        config=FaissVectorStoreConfig(dimension=768)
    ),
    retrieval=_dense_search(top_k=3),
    generation=GenerationConfig(
        strategy=GenerationType.DEFAULT,
        provider='groq',
        config=DefaultGenerationConfig(
            model='llama-3.1-8b-instant',
            max_tokens=256,
            temperature=0.5
        )
    ),
    evaluation=EvaluationConfig(
        type=EvaluationType.TRACE,
        provider='groq',
        config=TRACeEvaluationConfig(model='llama-3.1-8b-instant')
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
    print("1. fast_local - Fast & local embeddings (Groq generation)")
    print("2. high_quality - High quality with reranking")
    print("3. openai_production - Production grade OpenAI")
    print("4. medical - Medical/scientific documents")
    print("5. cost_optimized - Cost optimized")

    config = get_config_by_name('high_quality')
    print(f"\nSelected: high_quality")
    print(f"Chunking: {config.chunking.type}")
    print(f"Embedding: {config.embedding.type}")
    print(f"Search strategies: {[s.type for s in config.retrieval.search.searches]}")
    print(f"Generation: {config.generation.strategy}")
    print(f"Evaluation: {config.evaluation.type}")
