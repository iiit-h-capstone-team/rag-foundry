from rag.config.config import NoOpFusionConfig
from rag.retrieval.fusion.base import FusionStrategy


class NoOpFusionStrategy(FusionStrategy):

    def __init__(self, config: NoOpFusionConfig):
        self.config = config

    def run(self, ctx):
        if not ctx.search_results:
            ctx.fused_results = []
            return ctx

        ctx.fused_results = list(ctx.search_results[0])
        return ctx
