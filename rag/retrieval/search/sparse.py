from rag.config.config import SparseSearchConfig
from rag.retrieval.search.base import SearchStrategy


class SparseSearchStrategy(SearchStrategy):

    def __init__(
        self,
        config: SparseSearchConfig,
        vector_store,
        bm25_store=None,
    ):
        self.config = config
        self.vector_store = vector_store
        self.bm25_store = bm25_store

    def search(self, query: str):
        if not self.bm25_store:
            return []

        sparse_scores = self.bm25_store.search(query, self.config.top_k)
        max_score = max([score for _, score in sparse_scores] + [1e-6])

        results = []
        for idx, score in sparse_scores:
            chunk_idx = int(idx)
            normalized_score = score / max_score
            results.append({
                "index": chunk_idx,
                "chunk": self.vector_store.chunks[chunk_idx],
                "score": float(normalized_score),
                "sparse_score": float(normalized_score),
            })

        return results
