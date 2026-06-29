"""Core data models and the report-strategy abstraction.

The reporting layer mirrors the rest of the codebase: a thin orchestrator
(``ReportGenerator``) delegates the actual work to interchangeable strategies
(``ReportStrategy``). A strategy turns the raw output of one or more pipeline
runs into a presentable :class:`Report`.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path
import json

import pandas as pd

from rag.models.pipeline_run_result import PipelineRunResult

@dataclass
class ReportSection:
    """Rendered output for a single pipeline run."""

    config_name: str
    per_query: pd.DataFrame
    summary: pd.DataFrame
    config_summary: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Report:
    """A complete report: one section per pipeline run."""

    title: str
    strategy_name: str
    sections: List[ReportSection]

    @property
    def config_name(self) -> str:
        """Get the config name from the first section.
        
        Convenience property for single-section reports (typical case).
        Raises ValueError if report has no sections.
        """
        if not self.sections:
            raise ValueError("Report has no sections")
        return self.sections[0].config_name

    def section_for(self, config_name: str) -> Optional[ReportSection]:
        for section in self.sections:
            if section.config_name == config_name:
                return section
        return None

    def save_json(self, path: str | Path) -> None:
        """Save the report as a JSON file."""

        data = {
            "title": self.title,
            "strategy_name": self.strategy_name,
            "sections": [
                {
                    "config_name": section.config_name,
                    "config_summary": section.config_summary,
                    "per_query": section.per_query.to_dict(orient="records"),
                    "summary": section.summary.to_dict(orient="records"),
                }
                for section in self.sections
            ],
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


    @classmethod
    def load_json(cls, path: str | Path) -> "Report":
        """Load a report previously saved with ``save_json``."""

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        sections = [
            ReportSection(
                config_name=section["config_name"],
                config_summary=section.get("config_summary", {}),
                per_query=pd.DataFrame(section["per_query"]),
                summary=pd.DataFrame(section["summary"]),
            )
            for section in data["sections"]
        ]

        return cls(
            title=data["title"],
            strategy_name=data["strategy_name"],
            sections=sections,
        )

    def display(self) -> None:
        """Render the report inside a notebook (falls back to ``print``)."""
        try:
            from IPython.display import display
            from IPython.display import Markdown

            def show(obj):
                display(obj)

            def heading(text):
                display(Markdown(text))
        except ImportError:
            def show(obj):
                print(obj)

            def heading(text):
                print(text)

        heading(f"# {self.title}")
        heading(f"_Strategy: {self.strategy_name}_")

        for section in self.sections:
            heading(f"## Config: `{section.config_name}`")
            if section.config_summary:
                summary_line = "  •  ".join(
                    f"**{key}**: {value}"
                    for key, value in section.config_summary.items()
                )
                heading(summary_line)

            heading("### Per-query results")
            show(section.per_query)

            heading("### Aggregate TRACe scores (mean / ground truth / deviation)")
            show(section.summary)

    @classmethod
    def from_jsonl(
        cls,
        jsonl_path: str | Path,
        config_name: str,
        *,
        title: str = "Experiment Report",
        strategy_name: str = "jsonl",
    ) -> "Report":
        jsonl_path = Path(jsonl_path)

        rows = []
        summary_rows = []

        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                record = json.loads(line)
                metadata = record.get("metadata", {})

                # Skip failed/incomplete runs
                if metadata.get("status") != "success":
                    continue

                predicted = metadata.get("predicted_scores")
                ground_truth = metadata.get("ground_truth")

                if predicted is None or ground_truth is None:
                    continue

                row = {
                    "query": record["query"],
                    "retrieved_documents": record["retrieved_docs"],
                    "answer": record["answer"],
                }

                for metric in (
                    "relevance_score",
                    "utilization_score",
                    "completeness_score",
                    "adherence_score",
                ):
                    pred = predicted[metric]
                    gt = ground_truth[metric]

                    row[f"{metric}__pred"] = pred
                    row[f"{metric}__gt"] = gt
                    row[f"{metric}__deviation"] = pred - gt

                rows.append(row)

        if not rows:
            raise ValueError(f"No successful records found in {jsonl_path}")

        per_query = pd.DataFrame(rows)

        summary = pd.DataFrame(
            [
                {
                    "metric": metric,
                    "mean": per_query[f"{metric}__pred"].mean(),
                    "ground_truth": per_query[f"{metric}__gt"].mean(),
                    "deviation": per_query[f"{metric}__deviation"].mean(),
                }
                for metric in (
                    "relevance_score",
                    "utilization_score",
                    "completeness_score",
                    "adherence_score",
                )
            ]
        )

        section = ReportSection(
            config_name=config_name,
            per_query=per_query,
            summary=summary,
            config_summary={},
        )

        return cls(
            title=title,
            strategy_name=strategy_name,
            sections=[section],
        )

class ReportStrategy(ABC):
    """Turn raw pipeline runs into a :class:`Report`.

    Concrete strategies decide what the report looks like (which columns,
    which aggregates, how documents are rendered). New report formats are added
    by implementing this interface, never by editing :class:`ReportGenerator`.
    """

    #: Stable identifier used to register and select the strategy.
    name: str = "base"

    @abstractmethod
    def build(self, runs: List[PipelineRunResult]) -> Report:
        """Build a report from one or more pipeline runs."""
        raise NotImplementedError
