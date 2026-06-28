from rag.retrieval.rerank.base import RetrievalRerankStage


def _resolve_top_k(config) -> int:
    return getattr(config, "top_k", None) or getattr(config, "top_n", 5)


class RerankerRetrievalStage(RetrievalRerankStage):

    def __init__(self, reranker, config):
        self.reranker = reranker
        self.config = config

    def run(self, ctx):
        if not ctx.fused_results:
            ctx.results = []
            return ctx

        query = ctx.transformed_query or ctx.query
        candidates = ctx.fused_results
        candidate_texts = [result["chunk"].text for result in candidates]

        if hasattr(self.reranker, "rerank"):
            rerank_scores = self.reranker.rerank(query, candidate_texts)
        else:
            rerank_scores = self.reranker.predict(
                [[query, text] for text in candidate_texts]
            )

        reranked = []
        for candidate, score in zip(candidates, rerank_scores):
            result = dict(candidate)
            result["rerank_score"] = float(score)
            reranked.append(result)

        top_k = _resolve_top_k(self.config)
        reranked.sort(key=lambda item: item["rerank_score"], reverse=True)
        ctx.results = reranked[:top_k]
        return ctx
