import faiss
import numpy as np

from rag.config.config import FaissVectorStoreConfig


class FaissVectorStore:

    def __init__(
        self,
        config: FaissVectorStoreConfig
    ):
        self.config = config

        self.index = faiss.IndexFlatIP(
            self.config.dimension
        )

        self.chunks = []

    def add(
        self,
        embeddings,
        chunks
    ):

        self.index.add(
            embeddings.astype(
                np.float32
            )
        )

        self.chunks.extend(
            chunks
        )

    def search(
        self,
        query_embedding,
        top_k
    ):

        return self.index.search(
            query_embedding,
            top_k
        )