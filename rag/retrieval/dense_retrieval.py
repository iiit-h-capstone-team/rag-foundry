from rag.retrieval.base import RetrievalStrategy


class DenseRetrievalStrategy(RetrievalStrategy):

    def __init__(
        self,
        embedder,
        vector_store,
        config
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.top_k = config.top_k

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
            self.top_k
        )

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= 0:
                results.append({
                    "chunk": self.vector_store.chunks[int(idx)],
                    "score": float(distance)
                })

        return results
