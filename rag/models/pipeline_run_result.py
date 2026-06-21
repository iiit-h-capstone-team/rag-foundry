from dataclasses import dataclass, field
from typing import Dict, Any, List

from rag.config.config import RAGConfig
from rag.models.query_result import QueryResult

@dataclass
class PipelineRunResult:
    """All per-query records for one config, plus a human-readable summary."""

    records: List[QueryResult]
    config: RAGConfig