from rag.retrieval.context import RetrievalContext
from rag.retrieval.fusion.base import FusionStrategy
from rag.retrieval.query_transform.base import QueryTransformStrategy
from rag.retrieval.rerank.base import RetrievalRerankStage
from rag.retrieval.search.pipeline import SearchPipeline


class RetrievalPipeline:
    """Orchestrates query transform, search, fusion, and rerank stages."""

    def __init__(
        self,
        query_transform: QueryTransformStrategy,
        search: SearchPipeline,
        fusion: FusionStrategy,
        rerank: RetrievalRerankStage,
    ):
        self.query_transform = query_transform
        self.search = search
        self.fusion = fusion
        self.rerank = rerank

    def retrieve(self, query: str) -> list[dict]:
        ctx = RetrievalContext(query=query)
        ctx = self.query_transform.run(ctx)
        ctx = self.search.run(ctx)
        ctx = self.fusion.run(ctx)
        ctx = self.rerank.run(ctx)
        return ctx.results
