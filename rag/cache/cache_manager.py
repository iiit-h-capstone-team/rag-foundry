"""Centralized cache subsystem.

``CacheManager`` is the single owner of all cache logic: it derives cache keys
from the stage lineage and config, and loads/saves payloads via
:class:`CacheStorage`. Chunkers, embedders and vector stores never touch cache
directories themselves — they stay pure, and the pipeline talks only to this
manager.

Lineage (a child key changes whenever its parent key or its own config changes)::

    chunk_cache_key     = hash(datasource_hash,    chunking_config_hash)
    embedding_cache_key = hash(chunk_cache_key,     embedding_config_hash)
    index_cache_key     = hash(embedding_cache_key, vectorstore_config_hash)

Retrieval config is intentionally absent from every key: changing retrieval
reuses the same index.
"""

import logging
from typing import List, Optional

import numpy as np

from rag.cache.hashing import combine_keys, hash_config, hash_documents
from rag.cache.models import CacheMetadata
from rag.cache.storage import CacheStorage
from rag.config.config import CacheConfig
from rag.models.chunk import Chunk

logger = logging.getLogger(__name__)


class CacheManager:
    """Compute cache keys and load/save chunk, embedding and index caches."""

    def __init__(self, config: CacheConfig):
        self.config = config
        self.enabled = config.enabled
        self.storage = CacheStorage(config.cache_dir)

    # ------------------------------------------------------------------
    # Hashing / key derivation
    # ------------------------------------------------------------------
    def datasource_hash(self, documents) -> str:
        return hash_documents(documents)

    def get_chunk_cache_key(self, datasource_hash: str, chunking_config) -> str:
        return combine_keys(datasource_hash, hash_config(chunking_config))

    def get_embedding_cache_key(self, chunk_cache_key: str, embedding_config) -> str:
        return combine_keys(chunk_cache_key, hash_config(embedding_config))

    def get_index_cache_key(self, embedding_cache_key: str, vector_store_config) -> str:
        return combine_keys(embedding_cache_key, hash_config(vector_store_config))

    # ------------------------------------------------------------------
    # Chunk cache
    # ------------------------------------------------------------------
    def load_chunk_cache(self, cache_key: str) -> Optional[List[Chunk]]:
        if not self.enabled or not self.storage.exists("chunk", cache_key):
            return None
        return self.storage.load_chunks(cache_key)

    def save_chunk_cache(
        self,
        cache_key: str,
        chunks: List[Chunk],
        datasource_hash: str,
        chunking_config,
    ) -> None:
        if not self.enabled:
            return
        metadata = CacheMetadata(
            cache_key=cache_key,
            cache_type="chunk",
            parent_cache_key=None,
            datasource_hash=datasource_hash,
            config_hash=hash_config(chunking_config),
        )
        self.storage.save_chunks(cache_key, chunks, metadata)

    # ------------------------------------------------------------------
    # Embedding cache
    # ------------------------------------------------------------------
    def load_embedding_cache(self, cache_key: str) -> Optional[np.ndarray]:
        if not self.enabled or not self.storage.exists("embedding", cache_key):
            return None
        return self.storage.load_embeddings(cache_key)

    def save_embedding_cache(
        self,
        cache_key: str,
        embeddings: np.ndarray,
        parent_cache_key: str,
        embedding_config,
    ) -> None:
        if not self.enabled:
            return
        metadata = CacheMetadata(
            cache_key=cache_key,
            cache_type="embedding",
            parent_cache_key=parent_cache_key,
            config_hash=hash_config(embedding_config),
        )
        self.storage.save_embeddings(cache_key, embeddings, metadata)

    # ------------------------------------------------------------------
    # Index cache
    # ------------------------------------------------------------------
    def load_index_cache(self, cache_key: str):
        if not self.enabled or not self.storage.exists("index", cache_key):
            return None
        return self.storage.load_index(cache_key)

    def save_index_cache(
        self,
        cache_key: str,
        index,
        parent_cache_key: str,
        vector_store_config,
    ) -> None:
        if not self.enabled:
            return
        metadata = CacheMetadata(
            cache_key=cache_key,
            cache_type="index",
            parent_cache_key=parent_cache_key,
            config_hash=hash_config(vector_store_config),
        )
        self.storage.save_index(cache_key, index, metadata)
