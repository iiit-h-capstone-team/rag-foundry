"""Reporting layer for RAG pipeline runs.

Exposes the report generator, the strategy interface, the bundled detailed
strategy, and the data models used to feed pipeline output into a report.
"""

from reporting.enums import ReportType


# Lazy imports to avoid pandas dependency at import time
def __getattr__(name):
    if name in ("Report", "ReportSection", "ReportStrategy"):
        from reporting.base import Report, ReportSection, ReportStrategy
        return {"Report": Report, "ReportSection": ReportSection, "ReportStrategy": ReportStrategy}[name]
    if name in ("report_registry", "ReportRegistry"):
        from reporting.registry import report_registry, ReportRegistry
        return {"report_registry": report_registry, "ReportRegistry": ReportRegistry}[name]
    if name == "DetailedQueryReportStrategy":
        from reporting.detailed_report import DetailedQueryReportStrategy
        return DetailedQueryReportStrategy
    if name == "ReportGenerator":
        from reporting.report_generator import ReportGenerator
        return ReportGenerator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Report",
    "ReportSection",
    "ReportStrategy",
    "ReportRegistry",
    "report_registry",
    "ReportType",
    "DetailedQueryReportStrategy",
    "ReportGenerator",
]
