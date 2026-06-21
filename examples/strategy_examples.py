"""
Example usage of all RAG strategies.
This demonstrates how to use each strategy type.
"""

from rag.factory.strategy_factory import StrategyFactory
from rag.config.config import (
    ChunkingConfig,
    EmbeddingConfig,
    VectorStoreConfig,
)
from rag.config.enums import (
    ChunkingType,
    EmbeddingType,
    VectorStoreType,
)
from rag.models.document import Document
import numpy as np


def example_chunking():
    """Example: Using different chunking strategies."""
    doc = Document(
        title="Sample Document",
        content="This is a sample document with multiple sentences. Each sentence can be processed differently depending on the chunking strategy used.",
        metadata={"source": "example"}
    )

    print("=== CHUNKING STRATEGIES ===\n")

    # Sentence chunking
    sentence_chunker = StrategyFactory.create_chunker(
        ChunkingConfig(type=ChunkingType.SENTENCE)
    )
    chunks = sentence_chunker.chunk(doc)
    print(f"Sentence Chunking: {len(chunks)} chunks")

    # Fixed window chunking
    fixed_chunker = StrategyFactory.create_chunker(
        ChunkingConfig(
            type=ChunkingType.FIXED_WINDOW,
            window_size=50,
            overlap=10
        )
    )
    chunks = fixed_chunker.chunk(doc)
    print(f"Fixed Window Chunking: {len(chunks)} chunks")

    # Token chunking
    token_chunker = StrategyFactory.create_chunker(
        ChunkingConfig(
            type=ChunkingType.TOKEN,
            max_tokens=10,
            overlap_tokens=2
        )
    )
    chunks = token_chunker.chunk(doc)
    print(f"Token Chunking: {len(chunks)} chunks\n")


def example_embedding():
    """Example: Using different embedding strategies."""
    print("=== EMBEDDING STRATEGIES ===\n")

    texts = [
        "This is a sample text.",
        "Another piece of text for embedding."
    ]

    # SentenceTransformer embedding (doesn't require API keys).
    # Any SentenceTransformer model works here, e.g. a BGE model name.
    local_embedder = StrategyFactory.create_embedder(
        EmbeddingConfig(
            type=EmbeddingType.SENTENCE_TRANSFORMER,
            model_name='sentence-transformers/all-MiniLM-L6-v2'
        )
    )
    embeddings = local_embedder.embed(texts)
    print(f"SentenceTransformer Embeddings shape: {np.array(embeddings).shape}")

    # Note: OpenAI embeddings would require an API client
    print("OpenAI embeddings require client initialization\n")


def example_vectorstore_and_retrieval():
    """Example: Using vector store and retrieval strategies."""
    print("=== VECTOR STORE & RETRIEVAL ===\n")

    # Create FAISS vector store
    vector_store = StrategyFactory.create_vectorstore(
        VectorStoreConfig(
            type=VectorStoreType.FAISS,
            dimension=384  # MiniLM dimension
        )
    )
    print("FAISS Vector Store created")

    # Generate sample embeddings
    sample_embeddings = np.random.randn(5, 384).astype(np.float32)
    from rag.models.chunk import Chunk
    sample_chunks = [
        Chunk(text=f"Sample text {i}", metadata={"id": i})
        for i in range(5)
    ]

    vector_store.add(sample_embeddings, sample_chunks)
    print(f"Added {len(sample_chunks)} chunks to vector store\n")


def example_generation():
    """Example: Using generation strategies."""
    print("=== GENERATION STRATEGIES ===\n")

    # Note: These require actual clients (Groq, OpenAI)
    # Here we show the factory pattern usage
    try:
        # This would require a registered provider:
        # from rag.config.config import GenerationConfig
        # from rag.config.enums import GenerationType
        # generator = StrategyFactory.create_generator(
        #     GenerationConfig(
        #         strategy=GenerationType.DEFAULT,
        #         provider='groq',
        #         model='llama-3.1-8b-instant',
        #     ),
        #     provider=ProviderManager.get_provider('groq'),
        # )
        print("Groq Generation Strategy - requires Groq API client")
        print("OpenAI Generation Strategy - requires OpenAI API client\n")
    except Exception as e:
        print(f"Generation strategies require API clients: {e}\n")


def example_evaluation():
    """Example: Using evaluation strategies."""
    print("=== EVALUATION STRATEGIES ===\n")

    # Note: TRACe evaluation requires a judge client
    try:
        # This would require a registered provider:
        # from rag.config.config import EvaluationConfig
        # from rag.config.enums import EvaluationType
        # evaluator = StrategyFactory.create_evaluator(
        #     EvaluationConfig(
        #         type=EvaluationType.TRACE,
        #         provider='groq',
        #         model='llama-3.3-70b-versatile',
        #     ),
        #     provider=ProviderManager.get_provider('groq'),
        # )
        print("TRACe Evaluation Strategy - requires judge LLM client\n")
    except Exception as e:
        print(f"Evaluation strategies require judge client: {e}\n")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("RAG STRATEGY EXAMPLES")
    print("="*50 + "\n")

    example_chunking()
    example_embedding()
    example_vectorstore_and_retrieval()
    example_generation()
    example_evaluation()

    print("="*50)
    print("All strategies demonstrated!")
    print("="*50)
