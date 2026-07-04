"""Search configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rag.modules.search.enums import SearchType


@dataclass
class BaseSearchConfig:
    """Base class for all search strategy configurations."""
    pass


@dataclass
class SearchStrategyConfig:
    """One search strategy entry inside the search sub-pipeline."""
    type: SearchType
    config: Any = None

    def __post_init__(self):
        self.type = SearchType(self.type)
        if self.config is None:
            self.config = {}


@dataclass
class SearchPipelineConfig:
    """Search sub-pipeline: one or more search strategies (mandatory)."""
    searches: list

    def __post_init__(self):
        if not self.searches:
            raise ValueError("search.searches must contain at least one search")
        self.searches = [
            item if isinstance(item, SearchStrategyConfig) else SearchStrategyConfig(**item)
            for item in self.searches
        ]
