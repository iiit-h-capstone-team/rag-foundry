import logging

import numpy as np

from rag.cache.cache_manager import CacheManager
from rag.chunking.chunking_factory import ChunkingFactory
from rag.config.config import RAGConfig
from rag.config.enums import Mode
from rag.embedding.embedding_factory import EmbeddingFactory
from rag.evaluation.evaluator_factory import EvaluatorFactory
from rag.generation.generator_factory import GeneratorFactory
from rag.models.document import Document
from providers.provider_manager import ProviderManager
from rag.retrieval.retrieval_factory import RetrievalFactory
from rag.vectorstores.vectorstore_factory import VectorStoreFactory

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

        # Centralized cache subsystem (chunk -> embedding -> index lineage).
        self.cache_manager = CacheManager(self.config.cache)

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
        self.chunker = ChunkingFactory.create_chunker(
            self.config.chunking
        )

        # Embedding
        self.embedder = EmbeddingFactory.create_embedder(
            self.config.embedding
        )

        # Vector Store
        self.vector_store = VectorStoreFactory.create_vectorstore(
            self.config.vector_store
        )

        # Retrieval pipeline
        self.retriever = RetrievalFactory.create_retrieval_pipeline(
            config=self.config.retrieval,
            embedder=self.embedder,
            vector_store=self.vector_store,
            bm25_store=None,
        )

        # Generation
        
        generation_provider = (
            ProviderManager.get_provider(
                self.config.generation.provider
            )
        )

        self.generator = GeneratorFactory.create_generator(
            config=self.config.generation,
            provider=generation_provider
        )

        # Evaluation
        evaluation_provider = (
            ProviderManager.get_provider(
                self.config.evaluation.provider
            )
        )
        self.evaluator = EvaluatorFactory.create_evaluator(
            config=self.config.evaluation,
            provider=evaluation_provider
        )

    def build_index(self, documents: list[Document]):
        """Build the vector index, reusing cached stages where possible.

        Each stage (chunking, embedding, indexing) is keyed on the previous
        stage's cache key plus its own config, so a change to any upstream stage
        or config transparently invalidates everything downstream while leaving
        existing caches untouched for other experiments.
        """
        logger.info("Processing %d documents...", len(documents))
        cache = self.cache_manager

        datasource_hash = cache.datasource_hash(documents)

        # 1. Chunking
        chunk_key = cache.get_chunk_cache_key(datasource_hash, self.config.chunking)
        chunks = cache.load_chunk_cache(chunk_key)
        if chunks is not None:
            logger.info("[Chunk Cache] HIT key=%s", chunk_key)
        else:
            logger.info("[Chunk Cache] MISS key=%s", chunk_key)
            chunks = []
            for doc in documents:
                chunks.extend(self.chunker.chunk(doc))
            cache.save_chunk_cache(
                chunk_key, chunks, datasource_hash, self.config.chunking
            )
        logger.debug("Chunk cache key=%s (%d chunks)", chunk_key, len(chunks))

        # 2. Embedding
        embedding_key = cache.get_embedding_cache_key(chunk_key, self.config.embedding)
        embeddings = cache.load_embedding_cache(embedding_key)
        if embeddings is not None:
            logger.info("[Embedding Cache] HIT key=%s", embedding_key)
        else:
            logger.info("[Embedding Cache] MISS key=%s", embedding_key)
            texts = [chunk.text for chunk in chunks]
            embeddings = self.embedder.embed(texts)
            embeddings = np.array(embeddings).astype('float32')
            cache.save_embedding_cache(
                embedding_key, embeddings, chunk_key, self.config.embedding
            )
        embeddings = np.asarray(embeddings).astype('float32')
        logger.debug("Embedding cache key=%s (%d vectors)", embedding_key, len(embeddings))

        # 3. Vector index (retrieval config is intentionally NOT part of the key)
        index_key = cache.get_index_cache_key(embedding_key, self.config.vector_store)
        cached_index = cache.load_index_cache(index_key)
        if cached_index is not None:
            logger.info("[Index Cache] HIT key=%s", index_key)
            self.vector_store.index = cached_index
            self.vector_store.chunks = list(chunks)
        else:
            logger.info("[Index Cache] MISS key=%s", index_key)
            self.vector_store.add(embeddings, chunks)
            cache.save_index_cache(
                index_key, self.vector_store.index, embedding_key, self.config.vector_store
            )
        logger.debug("Index cache key=%s", index_key)

        logger.info("Vector store ready with %d chunks", len(self.vector_store.chunks))

    def query(self, query: str) -> dict:
        """Run complete RAG query."""
        logger.info("Query: %s", query)

        # 1. Retrieve
        logger.debug("Retrieving documents...")
        retrieved = self.retriever.retrieve(query)
        logger.debug("Retrieved %d documents", len(retrieved))

        # Format for generation. Every score the retriever attached
        # (e.g. dense_score, rerank_score, score) is preserved alongside the
        # text/metadata so downstream consumers (reporting) keep full detail.
        retrieved_docs = []
        for r in retrieved:
            doc = {k: v for k, v in r.items() if k != "chunk"}
            doc["text"] = r["chunk"].text
            doc["metadata"] = r["chunk"].metadata
            retrieved_docs.append(doc)

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
