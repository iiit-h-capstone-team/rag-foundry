"""Report strategy types."""

from enum import Enum


class ReportType(str, Enum):
    """Available report strategies."""
    DETAILED_QUERY = "detailed_query"
