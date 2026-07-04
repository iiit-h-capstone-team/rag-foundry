"""Query transform strategy types."""

from enum import Enum


class QueryTransformType(str, Enum):
    """Available query transform strategies."""
    NOOP = "noop"
    HYDE = "hyde"
    MULTI_QUERY = "multi_query"
    STEP_BACK = "step_back"
