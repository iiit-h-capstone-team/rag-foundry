from rag.config.config import DenseSearchConfig
from rag.retrieval.search.base import SearchStrategy


class DenseSearchStrategy(SearchStrategy):

    def __init__(
        self,
        config: DenseSearchConfig,
        embedder,
        vector_store,
    ):
        self.config = config
        self.embedder = embedder
        self.vector_store = vector_store

    def search(self, query: str):
        query_embedding = self.embedder.embed(query)

        if hasattr(query_embedding[0], '__len__'):
            query_embedding = query_embedding[0]

        distances, indices = self.vector_store.search(
            query_embedding.reshape(1, -1),
            self.config.top_k
        )

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= 0:
                chunk_idx = int(idx)
                results.append({
                    "index": chunk_idx,
                    "chunk": self.vector_store.chunks[chunk_idx],
                    "score": float(distance),
                    "dense_score": float(distance),
                })

        return results
