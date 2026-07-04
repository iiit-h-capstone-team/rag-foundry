"""Sparse search strategy implementation."""

from rag.modules.search.base import SearchStrategy
from rag.modules.search.registry import search_registry
from rag.modules.search.enums import SearchType
from rag.modules.search.strategies.sparse.config import SparseSearchConfig


@search_registry.register(SearchType.SPARSE)
class SparseSearchStrategy(SearchStrategy):
    """Sparse (BM25) search strategy."""

    def __init__(
        self,
        config: SparseSearchConfig,
        vector_store,
        bm25_store=None,
    ):
        super().__init__(config)
        self.vector_store = vector_store
        self.bm25_store = bm25_store

    def search(self, queries: list[str]):
        if not self.bm25_store:
            return []

        all_results = {}
        
        for query in queries:
            sparse_scores = self.bm25_store.search(query, self.config.top_k)
            max_score = max([score for _, score in sparse_scores] + [1e-6])

            for idx, score in sparse_scores:
                chunk_idx = int(idx)
                normalized_score = score / max_score
                if chunk_idx not in all_results or normalized_score > all_results[chunk_idx]["score"]:
                    all_results[chunk_idx] = {
                        "index": chunk_idx,
                        "chunk": self.vector_store.chunks[chunk_idx],
                        "score": float(normalized_score),
                        "sparse_score": float(normalized_score),
                    }

        sorted_results = sorted(all_results.values(), key=lambda x: x["score"], reverse=True)[:self.config.top_k]
        return sorted_results
