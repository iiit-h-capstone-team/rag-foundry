"""
Example usage of all RAG strategies.
This demonstrates how to use each strategy type.
"""

from rag.factory.strategy_factory import StrategyFactory
from rag.config.enums import (
    ChunkingType,
    EmbeddingType,
    RetrievalType,
    GenerationType,
    EvaluationType,
    VectorStoreType
)
from rag.models.document import Document
from rag.vectorstores.faiss_store import FaissVectorStore
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
    sentence_chunker = StrategyFactory.create_chunker(ChunkingType.SENTENCE)
    chunks = sentence_chunker.chunk(doc)
    print(f"Sentence Chunking: {len(chunks)} chunks")

    # Fixed window chunking
    fixed_chunker = StrategyFactory.create_chunker(
        ChunkingType.FIXED_WINDOW,
        window_size=50,
        overlap=10
    )
    chunks = fixed_chunker.chunk(doc)
    print(f"Fixed Window Chunking: {len(chunks)} chunks")

    # Token chunking
    token_chunker = StrategyFactory.create_chunker(
        ChunkingType.TOKEN,
        max_tokens=10,
        overlap_tokens=2
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

    # Local embedding (doesn't require API keys)
    local_embedder = StrategyFactory.create_embedder(
        EmbeddingType.LOCAL,
        model_name='sentence-transformers/all-MiniLM-L6-v2'
    )
    embeddings = local_embedder.embed(texts)
    print(f"Local Embeddings shape: {np.array(embeddings).shape}")

    # Note: BGE and OpenAI examples would require models/clients
    print("BGE and OpenAI embeddings require model/client initialization\n")


def example_vectorstore_and_retrieval():
    """Example: Using vector store and retrieval strategies."""
    print("=== VECTOR STORE & RETRIEVAL ===\n")

    # Create FAISS vector store
    vector_store = StrategyFactory.create_vectorstore(
        VectorStoreType.FAISS,
        dimension=384  # MiniLM dimension
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
        # This would fail without actual Groq client
        # groq_gen = StrategyFactory.create_generator(
        #     GenerationType.GROQ,
        #     client=groq_client,
        #     model='llama-3.1-8b-instant'
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
        # This would work with actual Groq client
        # evaluator = StrategyFactory.create_evaluator(
        #     EvaluationType.TRACE,
        #     judge_client=groq_client,
        #     model='llama-3.3-70b-versatile'
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
