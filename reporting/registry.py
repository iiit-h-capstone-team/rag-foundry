"""Report strategy registry."""

from core.registry import BaseRegistry
from reporting.base import ReportStrategy


class ReportRegistry(BaseRegistry[ReportStrategy]):
    """Registry for report strategy plugins."""
    pass


report_registry = ReportRegistry()

from reporting.detailed_report import DetailedQueryReportStrategy

