"""Report generator: a thin orchestrator over report strategies.

It owns a registry of :class:`ReportStrategy` instances and delegates report
construction to the selected one. Multiple strategies can be registered; one is
marked as the default and used when ``generate`` is called without a name.
"""

from typing import Dict, List, Optional, Union

from rag.reporting.base import PipelineRunResult, Report, ReportStrategy


class ReportGenerator:
    """Build reports from pipeline runs using a pluggable strategy."""

    def __init__(self, strategy: Optional[ReportStrategy] = None):
        self._strategies: Dict[str, ReportStrategy] = {}
        self._default: Optional[str] = None
        if strategy is not None:
            self.register(strategy, default=True)

    def register(self, strategy: ReportStrategy, default: bool = False) -> "ReportGenerator":
        """Register a strategy under its ``name``; optionally make it default."""
        self._strategies[strategy.name] = strategy
        if default or self._default is None:
            self._default = strategy.name
        return self

    @property
    def strategies(self) -> List[str]:
        return list(self._strategies)

    def _resolve(self, strategy_name: Optional[str]) -> ReportStrategy:
        name = strategy_name or self._default
        if name is None:
            raise ValueError("No report strategy registered.")
        if name not in self._strategies:
            raise ValueError(
                f"Unknown report strategy '{name}'. "
                f"Registered: {self.strategies}"
            )
        return self._strategies[name]

    def generate(
        self,
        runs: Union[PipelineRunResult, List[PipelineRunResult]],
        strategy_name: Optional[str] = None,
    ) -> Report:
        """Generate a report from one run or a list of runs."""
        if isinstance(runs, PipelineRunResult):
            runs = [runs]
        return self._resolve(strategy_name).build(runs)
