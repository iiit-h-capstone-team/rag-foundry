"""Reporting layer for RAG pipeline runs.

Exposes the report generator, the strategy interface, the bundled detailed
strategy, and the data models used to feed pipeline output into a report.
"""

from reporting.base import (
    Report,
    ReportSection,
    ReportStrategy,
)
from reporting.detailed_report import DetailedQueryReportStrategy
from reporting.report_generator import ReportGenerator
from reporting.strategy_factory import ReportStrategyFactory

__all__ = [
    "Report",
    "ReportSection",
    "ReportStrategy",
    "DetailedQueryReportStrategy",
    "ReportGenerator",
    "ReportStrategyFactory",
]
