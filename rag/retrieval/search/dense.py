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

    def search(self, queries: list[str]):
        all_results = {}
        
        for query in queries:
            query_embedding = self.embedder.embed(query)

            if hasattr(query_embedding[0], '__len__'):
                query_embedding = query_embedding[0]

            distances, indices = self.vector_store.search(
                query_embedding.reshape(1, -1),
                self.config.top_k
            )

            for idx, distance in zip(indices[0], distances[0]):
                if idx >= 0:
                    chunk_idx = int(idx)
                    # Keep the best (lowest) distance for each chunk
                    if chunk_idx not in all_results or distance < all_results[chunk_idx]["score"]:
                        all_results[chunk_idx] = {
                            "index": chunk_idx,
                            "chunk": self.vector_store.chunks[chunk_idx],
                            "score": float(distance),
                            "dense_score": float(distance),
                        }

        # Sort by score and return top_k
        sorted_results = sorted(all_results.values(), key=lambda x: x["score"])[:self.config.top_k]
        return sorted_results
