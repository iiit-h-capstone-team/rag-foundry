"""Production-grade cache subsystem for the RAG framework.

Caches chunking, embedding and index outputs with a content-addressed lineage so
experiments reuse expensive computation. Caches are never auto-deleted: a cache
miss creates a new entry, a hit reuses an existing one, and many experiments can
safely share the same chunk/embedding/index caches.
"""

from rag.cache.cache_manager import CacheManager
from rag.cache.hashing import (
    combine_keys,
    hash_config,
    hash_documents,
    serialize_config,
    sha256_hex,
)
from rag.cache.models import CacheMetadata
from rag.cache.storage import CacheStorage

__all__ = [
    "CacheManager",
    "CacheStorage",
    "CacheMetadata",
    "hash_documents",
    "hash_config",
    "serialize_config",
    "combine_keys",
    "sha256_hex",
]
