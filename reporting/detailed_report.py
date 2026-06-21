"""Detailed per-query report strategy.

For each pipeline run it produces:

* a per-query table with the query, the retrieved documents (as an array of
  ``{text, ...scores}`` entries keeping *all* retrieval scores), the generated
  answer, and every TRACe score next to its dataset ground truth plus the
  per-query deviation; and
* an aggregate table holding, for each relevant TRACe score, the mean predicted
  score, the mean ground truth, the standard deviation of each, and the mean
  absolute error between prediction and ground truth.
"""

from typing import Any, Dict, List

import pandas as pd

from rag.reporting.base import (
    Report,
    ReportSection,
    ReportStrategy,
)

from rag.models.pipeline_run_result import PipelineRunResult


class DetailedQueryReportStrategy(ReportStrategy):
    """Per-query breakdown plus aggregate TRACe statistics."""

    name = "detailed_query"

    #: TRACe scores compared against ground truth. ``adherence_score`` is a
    #: boolean and is treated as 0/1 so it aggregates uniformly with the rest.
    DEFAULT_TRACE_METRICS = (
        "relevance_score",
        "utilization_score",
        "completeness_score",
        "adherence_score",
    )

    def __init__(
        self,
        trace_metrics: tuple = DEFAULT_TRACE_METRICS,
        doc_text_chars: int = 200,
        round_to: int = 4,
    ):
        self.trace_metrics = tuple(trace_metrics)
        self.doc_text_chars = doc_text_chars
        self.round_to = round_to

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _to_float(value: Any) -> float:
        """Coerce a score (including booleans) to a float, NaN if impossible."""
        if isinstance(value, bool):
            return float(value)
        try:
            return float(value)
        except (TypeError, ValueError):
            return float("nan")

    def _format_docs(self, retrieved_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Render retrieved docs as an array keeping all numeric scores."""
        formatted = []
        for doc in retrieved_docs:
            scores = {
                key: round(value, self.round_to)
                for key, value in doc.items()
                if isinstance(value, (int, float)) and not isinstance(value, bool)
            }
            text = doc.get("text", "")
            snippet = text[: self.doc_text_chars]
            if len(text) > self.doc_text_chars:
                snippet += "..."
            entry = {"text": snippet}
            entry.update(scores)
            formatted.append(entry)
        return formatted

    # ------------------------------------------------------------------
    # Tables
    # ------------------------------------------------------------------
    def _build_per_query_table(self, run: PipelineRunResult) -> pd.DataFrame:
        rows = []
        for record in run.records:
            row: Dict[str, Any] = {
                "query": record.query,
                "retrieved_documents": self._format_docs(record.retrieved_docs),
                "answer": record.answer,
            }
            for metric in self.trace_metrics:
                pred = self._to_float(record.metadata.predicted_scores.get(metric))
                gt = self._to_float(record.metadata.ground_truth_scores.get(metric))
                row[f"{metric}__pred"] = round(pred, self.round_to)
                row[f"{metric}__gt"] = round(gt, self.round_to)
                row[f"{metric}__deviation"] = round(pred - gt, self.round_to)
            rows.append(row)
        return pd.DataFrame(rows)

    def _build_summary_table(self, run: PipelineRunResult) -> pd.DataFrame:
        rows = []
        for metric in self.trace_metrics:
            preds = pd.Series(
                [self._to_float(r.metadata.predicted_scores.get(metric)) for r in run.records]
            )
            gts = pd.Series(
                [self._to_float(r.metadata.ground_truth_scores.get(metric)) for r in run.records]
            )
            abs_error = (preds - gts).abs()
            rows.append(
                {
                    "metric": metric,
                    "mean_score": round(preds.mean(), self.round_to),
                    "mean_ground_truth": round(gts.mean(), self.round_to),
                    "std_score": round(preds.std(ddof=0), self.round_to),
                    "std_ground_truth": round(gts.std(ddof=0), self.round_to),
                    "mean_abs_error": round(abs_error.mean(), self.round_to),
                }
            )
        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Strategy entry point
    # ------------------------------------------------------------------
    def build(self, runs: List[PipelineRunResult]) -> Report:
        sections = [
            ReportSection(
                config_name=run.config.name,
                per_query=self._build_per_query_table(run),
                summary=self._build_summary_table(run),
                config_summary=run.config.model_dump(),
            )
            for run in runs
        ]
        return Report(
            title="RAG Multi-Config Evaluation Report",
            strategy_name=self.name,
            sections=sections,
        )
