from rag.config.config import HybridRetrievalConfig
from rag.retrieval.base import RetrievalStrategy


class HybridRetrievalStrategy(RetrievalStrategy):

    def __init__(
        self,
        config: HybridRetrievalConfig,
        embedder,
        vector_store,
        bm25_store=None
    ):
        self.config = config
        self.embedder = embedder
        self.vector_store = vector_store
        self.bm25_store = bm25_store

    def retrieve(
        self,
        query: str
    ):
        top_k = self.config.top_k
        dense_weight = self.config.dense_weight
        sparse_weight = self.config.sparse_weight

        query_embedding = self.embedder.embed(query)

        if hasattr(query_embedding[0], '__len__'):
            query_embedding = query_embedding[0]

        dense_distances, dense_indices = self.vector_store.search(
            query_embedding.reshape(1, -1),
            top_k * 2
        )

        dense_results = {}
        for rank, (idx, score) in enumerate(zip(dense_indices[0], dense_distances[0])):
            if idx >= 0:
                normalized_score = score / (max(dense_distances[0]) + 1e-6)
                dense_results[int(idx)] = dense_weight * normalized_score

        sparse_results = {}
        if self.bm25_store:
            sparse_scores = self.bm25_store.search(query, top_k * 2)
            for idx, score in sparse_scores:
                normalized_score = score / max([s for _, s in sparse_scores] + [1e-6])
                sparse_results[int(idx)] = sparse_weight * normalized_score

        combined_scores = {}
        for idx in set(dense_results.keys()) | set(sparse_results.keys()):
            combined_scores[idx] = dense_results.get(idx, 0) + sparse_results.get(idx, 0)

        sorted_indices = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        results = [
            {
                "chunk": self.vector_store.chunks[idx],
                "hybrid_score": score
            }
            for idx, score in sorted_indices
        ]

        return results
