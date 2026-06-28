from dataclasses import dataclass, field


@dataclass
class RetrievalContext:
    """Shared state passed between retrieval pipeline stages."""

    query: str
    transformed_query: str | None = None
    search_results: list[list[dict]] = field(default_factory=list)
    fused_results: list[dict] = field(default_factory=list)
    results: list[dict] = field(default_factory=list)
