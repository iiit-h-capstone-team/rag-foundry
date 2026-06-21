"""Reporting layer for RAG pipeline runs.

Exposes the report generator, the strategy interface, the bundled detailed
strategy, and the data models used to feed pipeline output into a report.
"""

from rag.reporting.base import (
    PipelineRunResult,
    QueryRecord,
    Report,
    ReportSection,
    ReportStrategy,
)
from rag.reporting.detailed_report import DetailedQueryReportStrategy
from rag.reporting.report_generator import ReportGenerator

__all__ = [
    "PipelineRunResult",
    "QueryRecord",
    "Report",
    "ReportSection",
    "ReportStrategy",
    "DetailedQueryReportStrategy",
    "ReportGenerator",
]
