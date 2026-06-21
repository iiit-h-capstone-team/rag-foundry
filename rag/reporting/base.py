"""Core data models and the report-strategy abstraction.

The reporting layer mirrors the rest of the codebase: a thin orchestrator
(``ReportGenerator``) delegates the actual work to interchangeable strategies
(``ReportStrategy``). A strategy turns the raw output of one or more pipeline
runs into a presentable :class:`Report`.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd


@dataclass
class QueryRecord:
    """Everything produced for a single query by a single pipeline.

    ``predicted_scores`` holds the TRACe scores returned by the pipeline's
    evaluator; ``ground_truth_scores`` holds the reference scores that ship with
    the dataset for the same query.
    """

    query: str
    retrieved_docs: List[Dict[str, Any]]
    answer: str
    predicted_scores: Dict[str, Any]
    ground_truth_scores: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineRunResult:
    """All per-query records for one config, plus a human-readable summary."""

    config_name: str
    records: List[QueryRecord]
    config_summary: Dict[str, Any] = field(default_factory=dict)


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

    def section_for(self, config_name: str) -> Optional[ReportSection]:
        for section in self.sections:
            if section.config_name == config_name:
                return section
        return None

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
