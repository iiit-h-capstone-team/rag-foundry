from rag.config.config import NoOpQueryTransformConfig
from rag.retrieval.query_transform.base import QueryTransformStrategy


class NoOpQueryTransformStrategy(QueryTransformStrategy):

    def __init__(self, config: NoOpQueryTransformConfig):
        self.config = config

    def run(self, ctx):
        ctx.transformed_query = ctx.query
        return ctx
