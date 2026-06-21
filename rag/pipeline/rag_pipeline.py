import logging

import numpy as np

from rag.config.config import RAGConfig
from rag.config.enums import Mode
from rag.factory.strategy_factory import StrategyFactory
from rag.models.document import Document
from providers.provider_manager import ProviderManager

logger = logging.getLogger(__name__)

# Per-mode logging verbosity:
#   dev  -> everything (DEBUG)
#   prod -> warnings and errors only
#   test -> errors only (quietest)
_MODE_LOG_LEVELS = {
    Mode.DEV: logging.DEBUG,
    Mode.PROD: logging.WARNING,
    Mode.TEST: logging.ERROR,
}


def _configure_logging(mode: Mode) -> None:
    """Set the ``rag`` logger level (and a handler) for the given mode."""
    rag_logger = logging.getLogger("rag")
    rag_logger.setLevel(_MODE_LOG_LEVELS[mode])
    if not rag_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        rag_logger.addHandler(handler)
    rag_logger.propagate = False


class RAGPipeline:
    """Complete RAG pipeline using configuration.

    Pure orchestrator: it knows only which strategy to build, the config object
    for that strategy, and the runtime dependencies. It never expands or reads
    individual strategy parameters — every strategy reads its own settings from
    its config object.
    """

    def __init__(self, config: RAGConfig):
        """
        Initialize RAG pipeline from configuration.

        Args:
            config: RAGConfig instance
        """
        self.config = config

        _configure_logging(self.config.mode)
        logger.debug("Initializing RAG pipeline in %s mode", self.config.mode.value)

        # Create strategies from config
        self._initialize_providers()
        self._initialize_strategies()

    def _initialize_providers(self):
        """
        Create all providers declared in config.
        Reuses existing instances through ProviderManager.
        """

        for provider_name, provider_config in (
            self.config.providers.items()
        ):

            ProviderManager.register(
                provider_name=provider_name,
                provider_type=provider_config.type,
                config=provider_config
            )


    def _initialize_strategies(self):
        """Initialize all strategies from config."""

        # Chunking
        self.chunker = StrategyFactory.create_chunker(
            self.config.chunking
        )

        # Embedding
        self.embedder = StrategyFactory.create_embedder(
            self.config.embedding
        )

        # Vector Store
        self.vector_store = StrategyFactory.create_vectorstore(
            self.config.vector_store
        )

        # Reranking (only used by rerank-based retrievers).
        self.reranker = (
            StrategyFactory.create_reranker(self.config.reranker)
            if self.config.reranker
            else None
        )

        # Retrieval
        self.retriever = StrategyFactory.create_retriever(
            config=self.config.retrieval,
            embedder=self.embedder,
            vector_store=self.vector_store,
            reranker=self.reranker,
            bm25_store=None,
        )

        # Generation
        
        generation_provider = (
            ProviderManager.get_provider(
                self.config.generation.provider
            )
        )

        self.generator = StrategyFactory.create_generator(
            config=self.config.generation,
            provider=generation_provider
        )

        # Evaluation
        evaluation_provider = (
            ProviderManager.get_provider(
                self.config.evaluation.provider
            )
        )
        self.evaluator = StrategyFactory.create_evaluator(
            config=self.config.evaluation,
            provider=evaluation_provider
        )

    def build_index(self, documents: list[Document]):
        """Build vector index from documents."""
        logger.info("Processing %d documents...", len(documents))

        all_chunks = []
        for doc in documents:
            chunks = self.chunker.chunk(doc)
            all_chunks.extend(chunks)

        logger.info("Created %d chunks", len(all_chunks))

        # Generate embeddings
        texts = [chunk.text for chunk in all_chunks]
        logger.info("Generating embeddings for %d chunks...", len(texts))
        embeddings = self.embedder.embed(texts)
        embeddings = np.array(embeddings).astype('float32')

        # Add to vector store
        self.vector_store.add(embeddings, all_chunks)
        logger.info("Vector store ready with %d chunks", len(all_chunks))

    def query(self, query: str) -> dict:
        """Run complete RAG query."""
        logger.info("Query: %s", query)

        # 1. Retrieve
        logger.debug("Retrieving documents...")
        retrieved = self.retriever.retrieve(query)
        logger.debug("Retrieved %d documents", len(retrieved))

        # Format for generation
        retrieved_docs = [
            {
                "text": r["chunk"].text,
                "metadata": r["chunk"].metadata
            }
            for r in retrieved
        ]

        # 2. Generate
        logger.debug("Generating response...")
        context = "\n\n".join([
            f"[Document {i+1}]\n{doc['text']}"
            for i, doc in enumerate(retrieved_docs)
        ])

        response = self.generator.generate(
            query=query,
            context=context,
        )
        logger.debug("Response generated (%d chars)", len(response))

        # 3. Evaluate
        logger.debug("Evaluating response...")
        scores = self.evaluator.evaluate(
            query=query,
            retrieved_docs=retrieved_docs,
            response=response,
        )
        logger.debug("Evaluation complete")

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
