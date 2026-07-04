"""FAISS vector store strategy implementation."""

import faiss
import numpy as np

from vectorstore.base import VectorStoreStrategy
from vectorstore.registry import vectorstore_registry
from vectorstore.enums import VectorStoreType
from vectorstore.strategies.faiss.config import FaissVectorStoreConfig


@vectorstore_registry.register(VectorStoreType.FAISS)
class FaissVectorStoreStrategy(VectorStoreStrategy):
    """FAISS vector store strategy."""

    def __init__(self, config: FaissVectorStoreConfig):
        super().__init__(config)
        self.index = faiss.IndexFlatIP(self.config.dimension)
        self.chunks = []

    def add(self, embeddings, chunks):
        self.index.add(embeddings.astype(np.float32))
        self.chunks.extend(chunks)

    def search(self, query_embedding, top_k):
        return self.index.search(query_embedding, top_k)
