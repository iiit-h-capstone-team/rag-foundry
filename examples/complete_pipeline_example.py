"""
Complete RAG pipeline using configuration system.
Shows how to use RAGConfig with strategies and factory.
"""

from rag.config.config import RAGConfig
from rag.config.loader import ConfigLoader
from rag.config.examples import get_config_by_name
from rag.factory.strategy_factory import StrategyFactory
from rag.models.document import Document
from rag.vectorstores.faiss_store import FaissVectorStore
import numpy as np


class RAGPipeline:
    """Complete RAG pipeline using configuration."""

    def __init__(self, config: RAGConfig, clients: dict):
        """
        Initialize RAG pipeline from configuration.

        Args:
            config: RAGConfig instance
            clients: Dict with 'groq' and/or 'openai' clients
        """
        self.config = config
        self.clients = clients

        # Create strategies from config
        self._initialize_strategies()

    def _initialize_strategies(self):
        """Initialize all strategies from config."""

        # Chunking
        self.chunker = StrategyFactory.create_chunker(
            self.config.chunking.type,
            max_words=self.config.chunking.max_words,
            overlap_sentences=self.config.chunking.overlap_sentences,
            window_size=self.config.chunking.window_size,
            overlap=self.config.chunking.overlap,
            max_tokens=self.config.chunking.max_tokens,
            overlap_tokens=self.config.chunking.overlap_tokens
        )

        # Embedding
        self.embedder = StrategyFactory.create_embedder(
            self.config.embedding.type,
            model_name=self.config.embedding.model_name,
            client=self.clients.get('openai') if self.config.embedding.type.value == 'openai' else None
        )

        # Vector Store
        self.vector_store = StrategyFactory.create_vectorstore(
            self.config.vector_store.type,
            dimension=self.config.embedding.dimension
        )

        # Retrieval
        self.retriever = StrategyFactory.create_retriever(
            self.config.retrieval.type,
            embedder=self.embedder,
            vector_store=self.vector_store,
            reranker=self.clients.get('reranker'),
            initial_k=self.config.retrieval.initial_k,
            dense_weight=self.config.retrieval.dense_weight,
            sparse_weight=self.config.retrieval.sparse_weight,
            bm25_store=self.clients.get('bm25_store')
        )

        # Generation
        gen_client = self.clients.get('groq') if self.config.generation.type.value == 'groq' else self.clients.get('openai')
        self.generator = StrategyFactory.create_generator(
            self.config.generation.type,
            client=gen_client,
            model=self.config.generation.model
        )

        # Evaluation
        eval_client = self.clients.get('groq') or self.clients.get('openai')
        self.evaluator = StrategyFactory.create_evaluator(
            self.config.evaluation.type,
            judge_client=eval_client,
            model=self.config.evaluation.model
        )

    def build_index(self, documents: list[Document]):
        """Build vector index from documents."""
        print(f"Processing {len(documents)} documents...")

        all_chunks = []
        for doc in documents:
            chunks = self.chunker.chunk(doc)
            all_chunks.extend(chunks)

        print(f"Created {len(all_chunks)} chunks")

        # Generate embeddings
        texts = [chunk.text for chunk in all_chunks]
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedder.embed(texts)
        embeddings = np.array(embeddings).astype('float32')

        # Add to vector store
        self.vector_store.add(embeddings, all_chunks)
        print(f"Vector store ready with {len(all_chunks)} chunks")

    def query(self, query: str, top_k: int = None) -> dict:
        """Run complete RAG query."""
        if top_k is None:
            top_k = self.config.retrieval.top_k

        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)

        # 1. Retrieve
        print("\n[1] Retrieving documents...")
        retrieved = self.retriever.retrieve(query, top_k=top_k)
        print(f"Retrieved {len(retrieved)} documents")

        # Format for generation
        retrieved_docs = [
            {
                "text": r["chunk"].text,
                "metadata": r["chunk"].metadata
            }
            for r in retrieved
        ]

        # 2. Generate
        print("\n[2] Generating response...")
        context = "\n\n".join([
            f"[Document {i+1}]\n{doc['text']}"
            for i, doc in enumerate(retrieved_docs)
        ])

        response = self.generator.generate(
            query=query,
            context=context,
            max_tokens=self.config.generation.max_tokens,
            temperature=self.config.generation.temperature
        )
        print(f"Response generated ({len(response)} chars)")

        # 3. Evaluate
        print("\n[3] Evaluating response...")
        scores = self.evaluator.evaluate(
            query=query,
            retrieved_docs=retrieved_docs,
            response=response
        )
        print(f"Evaluation complete")

        return {
            'query': query,
            'retrieved_docs': retrieved_docs,
            'response': response,
            'scores': scores
        }

    def print_results(self, result: dict):
        """Pretty print query results."""
        print(f"\n{'='*60}")
        print("QUERY RESULTS")
        print('='*60)

        print(f"\nQuery: {result['query']}")

        print(f"\n--- Retrieved Documents ({len(result['retrieved_docs'])}) ---")
        for i, doc in enumerate(result['retrieved_docs'][:3], 1):
            print(f"\n{i}. {doc['text'][:200]}...")

        print(f"\n--- Generated Response ---")
        print(result['response'][:500] + "..." if len(result['response']) > 500 else result['response'])

        print(f"\n--- TRACe Scores ---")
        scores = result['scores']
        print(f"  Relevance:    {scores['relevance_score']:.4f}")
        print(f"  Utilization:  {scores['utilization_score']:.4f}")
        print(f"  Completeness: {scores['completeness_score']:.4f}")
        print(f"  Adherence:    {scores['adherence_score']}")

        print(f"\n{'='*60}\n")


# ============================================================
# USAGE EXAMPLES
# ============================================================

if __name__ == "__main__":

    # Example 1: Load pre-built configuration
    print("Loading high quality configuration...")
    config = get_config_by_name('high_quality')

    # Example 2: Load from file
    # config = ConfigLoader.load('config/rag_config_high_quality.yaml')

    # Example 3: Create custom configuration
    # from rag.config.config import RAGConfig, GenerationConfig, EvaluationConfig
    # config = RAGConfig(
    #     # ... all configs ...
    #     generation=GenerationConfig(...),
    #     evaluation=EvaluationConfig(...)
    # )

    print("\nConfiguration loaded:")
    print(f"  Chunking:   {config.chunking.type.value}")
    print(f"  Embedding:  {config.embedding.type.value}")
    print(f"  Retrieval:  {config.retrieval.type.value}")
    print(f"  Generation: {config.generation.type.value} ({config.generation.model})")
    print(f"  Evaluation: {config.evaluation.type.value} ({config.evaluation.model})")

    # Initialize pipeline (requires actual clients)
    # clients = {
    #     'groq': groq_client,
    #     'openai': openai_client,
    #     'reranker': rerank_model
    # }
    #
    # pipeline = RAGPipeline(config, clients)
    #
    # # Build index
    # documents = [
    #     Document(title="Doc 1", content="...", metadata={})
    # ]
    # pipeline.build_index(documents)
    #
    # # Query
    # result = pipeline.query("Your question here?")
    # pipeline.print_results(result)
    #
    # # Batch query
    # queries = ["Question 1?", "Question 2?"]
    # for q in queries:
    #     result = pipeline.query(q)
    #     pipeline.print_results(result)

    print("\n✅ Configuration system ready!")
    print("Update the 'clients' dict with actual API clients and run pipeline")
