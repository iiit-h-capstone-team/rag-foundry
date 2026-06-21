"""Filesystem storage backend for the cache subsystem.

Owns the on-disk layout and (de)serialization of each payload type. Writes are
made durable by writing payload first and ``metadata.json`` last: an entry is
only considered valid when *both* the payload and its metadata exist, so a
crashed write never looks like a hit.

Layout::

    <cache_dir>/
    ├── chunks/<key>/{chunks.pkl, metadata.json}
    ├── embeddings/<key>/{embeddings.npy, metadata.json}
    └── indexes/<key>/{faiss.index, metadata.json}
"""

import json
import os
import pickle
from pathlib import Path
from typing import List, Optional

import numpy as np

from rag.cache.models import CacheMetadata
from rag.models.chunk import Chunk

# Maps logical cache type -> on-disk subdirectory and payload filename.
_LAYOUT = {
    "chunk": ("chunks", "chunks.pkl"),
    "embedding": ("embeddings", "embeddings.npy"),
    "index": ("indexes", "faiss.index"),
}

_METADATA_FILE = "metadata.json"


class CacheStorage:
    """Read/write cache payloads and metadata under a root directory."""

    def __init__(self, cache_dir: str):
        self.root = Path(cache_dir)

    def entry_dir(self, cache_type: str, cache_key: str) -> Path:
        subdir, _ = _LAYOUT[cache_type]
        return self.root / subdir / cache_key

    def _payload_path(self, cache_type: str, cache_key: str) -> Path:
        _, filename = _LAYOUT[cache_type]
        return self.entry_dir(cache_type, cache_key) / filename

    def _metadata_path(self, cache_type: str, cache_key: str) -> Path:
        return self.entry_dir(cache_type, cache_key) / _METADATA_FILE

    def exists(self, cache_type: str, cache_key: str) -> bool:
        """A valid entry requires both its payload and its metadata."""
        return (
            self._payload_path(cache_type, cache_key).exists()
            and self._metadata_path(cache_type, cache_key).exists()
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    @staticmethod
    def _atomic_write_bytes(path: Path, data: bytes) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    def _write_metadata(self, cache_type: str, cache_key: str, metadata: CacheMetadata) -> None:
        payload = json.dumps(metadata.to_dict(), indent=2).encode("utf-8")
        self._atomic_write_bytes(self._metadata_path(cache_type, cache_key), payload)

    def load_metadata(self, cache_type: str, cache_key: str) -> Optional[CacheMetadata]:
        path = self._metadata_path(cache_type, cache_key)
        if not path.exists():
            return None
        with open(path, "r") as f:
            return CacheMetadata.from_dict(json.load(f))

    # ------------------------------------------------------------------
    # Chunks
    # ------------------------------------------------------------------
    def save_chunks(self, cache_key: str, chunks: List[Chunk], metadata: CacheMetadata) -> None:
        self.entry_dir("chunk", cache_key).mkdir(parents=True, exist_ok=True)
        self._atomic_write_bytes(
            self._payload_path("chunk", cache_key),
            pickle.dumps(chunks, protocol=pickle.HIGHEST_PROTOCOL),
        )
        self._write_metadata("chunk", cache_key, metadata)

    def load_chunks(self, cache_key: str) -> List[Chunk]:
        with open(self._payload_path("chunk", cache_key), "rb") as f:
            return pickle.load(f)

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------
    def save_embeddings(self, cache_key: str, embeddings: np.ndarray, metadata: CacheMetadata) -> None:
        self.entry_dir("embedding", cache_key).mkdir(parents=True, exist_ok=True)
        path = self._payload_path("embedding", cache_key)
        tmp = path.with_name(path.name + ".tmp")
        with open(tmp, "wb") as f:
            np.save(f, np.asarray(embeddings))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        self._write_metadata("embedding", cache_key, metadata)

    def load_embeddings(self, cache_key: str) -> np.ndarray:
        return np.load(self._payload_path("embedding", cache_key))

    # ------------------------------------------------------------------
    # Index (FAISS)
    # ------------------------------------------------------------------
    def save_index(self, cache_key: str, index, metadata: CacheMetadata) -> None:
        import faiss

        self.entry_dir("index", cache_key).mkdir(parents=True, exist_ok=True)
        path = self._payload_path("index", cache_key)
        tmp = path.with_suffix(".index.tmp")
        faiss.write_index(index, str(tmp))
        os.replace(tmp, path)
        self._write_metadata("index", cache_key, metadata)

    def load_index(self, cache_key: str):
        import faiss

        return faiss.read_index(str(self._payload_path("index", cache_key)))
