import logging
import time
import traceback
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np

from rag.cache.cache_manager import CacheManager
from rag.modules.chunking import chunking_registry
from embedding import embedding_registry
from rag.config.config import RAGConfig
from rag.config.enums import Mode
from rag.modules.generation import generation_registry, GenerationType
from rag.models.document import Document
from rag.models.query_result import QueryResult
from providers.provider_manager import ProviderManager
from rag.modules.reranking import reranking_registry
from vectorstore import vectorstore_registry
from rag.modules.query_transform import query_transform_registry
from rag.modules.search import search_registry, SearchPipelineConfig
from rag.modules.fusion import fusion_registry
from rag.pipeline.retrieval_pipeline import RetrievalPipeline
from rag.pipeline.search_pipeline import SearchPipeline

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

    def __init__(self, config: RAGConfig, jsonl_path: Optional[Path] = None):
        """
        Initialize RAG pipeline from configuration.

        Args:
            config: RAGConfig instance
            jsonl_path: Optional path for JSONL output. If None, defaults to temp/{config.name}.jsonl
        """
        self.config = config
        self.jsonl_path = jsonl_path or Path("temp") / f"{config.name}.jsonl"

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
        self.chunker = chunking_registry.create(
            self.config.chunking.type,
            config=self.config.chunking.config
        )

        # Embedding
        self.embedder = embedding_registry.create(
            self.config.embedding.type,
            config=self.config.embedding.config
        )

        # Vector Store
        self.vector_store = vectorstore_registry.create(
            self.config.vector_store.type,
            config=self.config.vector_store.config
        )

        # Retrieval pipeline
        # Query transform
        query_transform_config = self.config.retrieval.query_transform
        provider = None
        if query_transform_config and query_transform_config.provider:
            provider_config = self.config.providers.get(query_transform_config.provider)
            if provider_config:
                provider = ProviderManager.get_provider(query_transform_config.provider)
        
        query_transform = query_transform_registry.create(
            query_transform_config.type if query_transform_config else "noop",
            config=query_transform_config.config if query_transform_config else {},
            provider=provider
        )

        # Search pipeline
        # BM25 store is built lazily during build_index; pass a
        # callable so sparse strategies can resolve it at search time.
        self.bm25_store = None
        search_strategies = []
        for search_config in self.config.retrieval.search.searches:
            strategy = search_registry.create(
                search_config.type,
                config=search_config.config,
                embedder=self.embedder,
                vector_store=self.vector_store,
                bm25_store=lambda: self.bm25_store,
            )
            search_strategies.append(strategy)
        
        search_pipeline = SearchPipeline(search_strategies)

        # Fusion
        fusion_config = self.config.retrieval.fusion
        fusion = fusion_registry.create(
            fusion_config.type if fusion_config else "noop",
            config=fusion_config.config if fusion_config else {}
        )

        # Reranker (optional)
        reranker = None
        if self.config.retrieval.rerank:
            rerank_config = self.config.retrieval.rerank
            rerank_provider = ProviderManager.get_provider(
                self.config.providers.get(list(self.config.providers.keys())[0]).type.value
            ) if self.config.providers else None
            reranker = reranking_registry.create(
                rerank_config.type,
                config=rerank_config.config,
                provider=rerank_provider
            )

        self.retriever = RetrievalPipeline(
            query_transform=query_transform,
            search_pipeline=search_pipeline,
            fusion=fusion,
            reranker=reranker,
        )

        # Generation
        generation_provider = ProviderManager.get_provider(
            self.config.generation.provider
        )

        self.generator = generation_registry.create(
            self.config.generation.strategy,
            config=self.config.generation.config,
            provider=generation_provider
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

        # 4. BM25 index (for sparse search)
        has_sparse = any(
            sc.type in ("sparse", "bm25")
            for sc in self.config.retrieval.search.searches
        )
        if has_sparse:
            from rag.modules.search.bm25_store import BM25Store
            self.bm25_store = BM25Store(chunks)
            logger.info("BM25 store ready with %d chunks", len(chunks))

    def query(self, query: str, query_index: int = 0, ground_truth: Optional[Dict] = None) -> QueryResult:
        """Run complete RAG query and return QueryResult with latencies."""
        logger.info("Query: %s", query)

        total_start = time.time()
        metadata = {}
        
        try:
            # 1. Retrieve
            logger.debug("Retrieving documents...")
            retrieval_start = time.time()
            retrieved = self.retriever.retrieve(query)
            retrieval_ms = (time.time() - retrieval_start) * 1000
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
            generation_start = time.time()
            context = "\n\n".join([
                f"[Document {i+1}]\n{doc['text']}"
                for i, doc in enumerate(retrieved_docs)
            ])

            response = self.generator.generate(
                query=query,
                context=context,
            )
            generation_ms = (time.time() - generation_start) * 1000
            logger.debug("Response generated (%d chars)", len(response))

            total_ms = (time.time() - total_start) * 1000

            # Store latencies and metadata
            metadata["latencies"] = {
                "retrieval_ms": retrieval_ms,
                "generation_ms": generation_ms,
                "total_ms": total_ms
            }
            metadata["query_index"] = query_index
            metadata["status"] = "success"
            
            if ground_truth:
                metadata["ground_truth"] = ground_truth

            # Convert retrieved_docs dict format to Document objects for QueryResult
            from rag.models.document import Document
            retrieved_doc_objects = [
                Document(
                    title=doc.get("title", ""),
                    content=doc.get("text", ""),
                    metadata=doc.get("metadata", {})
                )
                for doc in retrieved_docs
            ]

            return QueryResult(
                query=query,
                retrieved_docs=retrieved_doc_objects,
                answer=response,
                metadata=metadata
            )

        except Exception as e:
            total_ms = (time.time() - total_start) * 1000
            logger.error(f"Query failed: {e}")
            
            metadata["latencies"] = {
                "total_ms": total_ms
            }
            metadata["query_index"] = query_index
            metadata["status"] = "failed"
            metadata["error"] = traceback.format_exc()
            metadata["error_type"] = type(e).__name__
            
            if ground_truth:
                metadata["ground_truth"] = ground_truth

            return QueryResult(
                query=query,
                retrieved_docs=[],
                answer="",
                metadata=metadata
            )

    def print_results(self, result: QueryResult):
        """Pretty print query results."""
        print(f"\n{'='*60}")
        print("QUERY RESULTS")
        print('='*60)

        print(f"\nQuery: {result.query}")

        print(f"\n--- Retrieved Documents ({len(result.retrieved_docs)}) ---")
        for i, doc in enumerate(result.retrieved_docs[:3], 1):
            print(f"\n{i}. {doc.content[:200]}...")

        print(f"\n--- Generated Response ---")
        print(result.answer[:500] + "..." if len(result.answer) > 500 else result.answer)

        if "latencies" in result.metadata:
            print(f"\n--- Latencies ---")
            latencies = result.metadata["latencies"]
            print(f"  Retrieval:    {latencies.get('retrieval_ms', 0):.2f}ms")
            print(f"  Generation:   {latencies.get('generation_ms', 0):.2f}ms")
            print(f"  Total:        {latencies.get('total_ms', 0):.2f}ms")

        print(f"\n{'='*60}\n")
