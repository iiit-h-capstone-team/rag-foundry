from rag.config.config import WeightedSumFusionConfig
from rag.retrieval.fusion.base import FusionStrategy


class WeightedSumFusionStrategy(FusionStrategy):

    def __init__(self, config: WeightedSumFusionConfig):
        self.config = config

    def run(self, ctx):
        weights = self.config.weights
        if not weights:
            weights = [1.0] * len(ctx.search_results)
        if len(weights) != len(ctx.search_results):
            raise ValueError(
                "fusion.weights length must match the number of search strategies"
            )

        combined_scores: dict[int, float] = {}
        representative: dict[int, dict] = {}

        for weight, ranked_list in zip(weights, ctx.search_results):
            if not ranked_list:
                continue

            max_score = max(result["score"] for result in ranked_list) + 1e-6
            for result in ranked_list:
                chunk_idx = result["index"]
                normalized_score = weight * (result["score"] / max_score)
                combined_scores[chunk_idx] = (
                    combined_scores.get(chunk_idx, 0.0) + normalized_score
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
            fused["fusion_score"] = float(score)
            ctx.fused_results.append(fused)

        return ctx
