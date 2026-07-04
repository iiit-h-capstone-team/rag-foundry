"""Query transform configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rag.modules.query_transform.enums import QueryTransformType


@dataclass
class BaseQueryTransformConfig:
    """Base class for all query transform strategy configurations."""
    pass


@dataclass
class QueryTransformConfig:
    """Query transform section: which strategy plus its own typed config."""
    type: QueryTransformType
    provider: str | None = None
    config: Any = None

    def __post_init__(self):
        self.type = QueryTransformType(self.type)
        if self.config is None:
            self.config = {}
