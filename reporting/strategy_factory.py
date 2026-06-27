"""Factory for creating report strategies.

This factory provides a centralized way to create report strategy instances
by name, following the factory pattern for extensibility.
"""

from typing import Dict, Type

from reporting.base import ReportStrategy
from reporting.detailed_report import DetailedQueryReportStrategy


class ReportStrategyFactory:
    """Factory for creating report strategy instances.
    
    This factory maintains a registry of available report strategies and
    provides a clean interface for creating instances by name.
    """
    
    _strategies: Dict[str, Type[ReportStrategy]] = {
        "detailed_query": DetailedQueryReportStrategy,
    }
    
    @classmethod
    def create_strategy(cls, strategy_name: str, **kwargs) -> ReportStrategy:
        """Create a report strategy instance by name.
        
        Args:
            strategy_name: Name of the strategy to create
            **kwargs: Additional arguments to pass to the strategy constructor
            
        Returns:
            ReportStrategy instance
            
        Raises:
            ValueError: If strategy name is not registered
        """
        if strategy_name not in cls._strategies:
            available = ", ".join(cls.available_strategies())
            raise ValueError(
                f"Unknown report strategy: {strategy_name}. "
                f"Available strategies: {available}"
            )
        
        strategy_class = cls._strategies[strategy_name]
        return strategy_class(**kwargs)
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[ReportStrategy]) -> None:
        """Register a new report strategy.
        
        Args:
            name: Name to register the strategy under
            strategy_class: Strategy class to register
        """
        cls._strategies[name] = strategy_class
    
    @classmethod
    def available_strategies(cls) -> list[str]:
        """Get list of available strategy names.
        
        Returns:
            List of registered strategy names
        """
        return list(cls._strategies.keys())
