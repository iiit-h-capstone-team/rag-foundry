from rag.retrieval.base import RetrievalStrategy


class DenseRerankRetrievalStrategy(RetrievalStrategy):

    def __init__(
        self,
        embedder,
        vector_store,
        reranker,
        initial_k: int = 20
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.reranker = reranker
        self.initial_k = initial_k

    def retrieve(
        self,
        query: str,
        top_k: int
    ):
        query_embedding = self.embedder.embed(query)

        if hasattr(query_embedding[0], '__len__'):
            query_embedding = query_embedding[0]

        distances, indices = self.vector_store.search(
            query_embedding.reshape(1, -1),
            self.initial_k
        )

        candidates = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= 0:
                candidates.append({
                    "index": int(idx),
                    "score": float(distance)
                })

        candidate_texts = [
            self.vector_store.chunks[c["index"]].text
            for c in candidates
        ]

        if hasattr(self.reranker, "rerank"):
            rerank_scores = self.reranker.rerank(query, candidate_texts)
        else:
            rerank_scores = self.reranker.predict(
                [[query, text] for text in candidate_texts]
            )

        for candidate, score in zip(candidates, rerank_scores):
            candidate["rerank_score"] = float(score)

        reranked = sorted(
            candidates,
            key=lambda x: x["rerank_score"],
            reverse=True
        )[:top_k]

        results = [
            {
                "chunk": self.vector_store.chunks[r["index"]],
                "dense_score": r["score"],
                "rerank_score": r["rerank_score"]
            }
            for r in reranked
        ]

        return results