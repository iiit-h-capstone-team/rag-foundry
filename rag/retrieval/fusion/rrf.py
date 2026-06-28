from rag.config.config import RRFFusionConfig
from rag.retrieval.fusion.base import FusionStrategy


class RRFFusionStrategy(FusionStrategy):

    def __init__(self, config: RRFFusionConfig):
        self.config = config

    def run(self, ctx):
        combined_scores: dict[int, float] = {}
        representative: dict[int, dict] = {}

        for ranked_list in ctx.search_results:
            for rank, result in enumerate(ranked_list):
                chunk_idx = result["index"]
                combined_scores[chunk_idx] = (
                    combined_scores.get(chunk_idx, 0.0)
                    + 1.0 / (self.config.k + rank + 1)
                )
                if chunk_idx not in representative:
                    representative[chunk_idx] = dict(result)

        sorted_indices = sorted(
            combined_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:self.config.top_k]

        ctx.fused_results = []
        for chunk_idx, score in sorted_indices:
            fused = dict(representative[chunk_idx])
            fused["score"] = float(score)
            fused["rrf_score"] = float(score)
            ctx.fused_results.append(fused)

        return ctx
