from rag.retrieval.rerank.base import RetrievalRerankStage


class NoOpRetrievalRerankStage(RetrievalRerankStage):

    def run(self, ctx):
        ctx.results = list(ctx.fused_results)
        return ctx
