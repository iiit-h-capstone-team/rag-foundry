"""Generic registry for plugin management."""

from typing import Callable, Dict, Any, TypeVar, Generic, Optional, Union, Type
from enum import Enum
import inspect

T = TypeVar("T")


class BaseRegistry(Generic[T]):
    """Generic registry for plugin registration and instantiation.
    
    Supports decorator-based registration, lookup, and creation of
    strategy instances. Prevents duplicate registrations and provides
    meaningful error messages.
    """

    def __init__(self):
        """Initialize empty registry."""
        self._strategies: Dict[str, Callable[..., T]] = {}

    def _normalize_key(self, key: Union[str, Enum]) -> str:
        """Convert enum or string key to string."""
        if isinstance(key, Enum):
            return key.value
        return key

    def register(self, key: Union[str, Enum]):
        """Decorator to register a strategy class.
        
        Decorates a strategy class and wraps it in a factory function.
        The decorator returns the factory function (not the class).
        
        Args:
            key: Unique identifier for the strategy (string or enum).
            
        Returns:
            Decorator function that wraps the class in a factory.
            
        Raises:
            ValueError: If key is already registered.
            
        Example:
            @registry.register(StrategyType.OPENAI)
            class OpenAIStrategy(BaseStrategy):
                def __init__(self, config):
                    super().__init__(config)
        """
        normalized_key = self._normalize_key(key)
        
        def decorator(strategy_class: Type[T]) -> Callable[..., T]:
            if normalized_key in self._strategies:
                raise ValueError(
                    f"Strategy '{normalized_key}' is already registered. "
                    f"Duplicate registration not allowed."
                )
            
            # Create factory function that instantiates the class.
            # Captures strategy_class via closure default to avoid
            # late-binding issues when multiple strategies are registered.
            def factory(_cls=strategy_class, **kwargs) -> T:
                # Auto-coerce dict configs to the typed dataclass declared
                # in the strategy's __init__ type hints.
                if "config" in kwargs and isinstance(kwargs["config"], dict):
                    import typing
                    import dataclasses
                    try:
                        hints = typing.get_type_hints(_cls.__init__)
                        config_cls = hints.get("config")
                        if config_cls and isinstance(config_cls, type):
                            cfg_dict = kwargs["config"]
                            if dataclasses.is_dataclass(config_cls):
                                field_names = {f.name for f in dataclasses.fields(config_cls)}
                                cfg_dict = {k: v for k, v in cfg_dict.items() if k in field_names}
                            kwargs["config"] = config_cls(**cfg_dict)
                    except Exception:
                        pass  # fall through with dict if resolution fails
                # Filter kwargs to only those accepted by the strategy's
                # __init__, so callers can pass a superset of resources
                # without breaking strategies that don't need them all.
                sig = inspect.signature(_cls.__init__)
                params = sig.parameters
                if not any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()):
                    accepted = {name for name, p in params.items()
                                if name != "self" and p.kind in (
                                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                    inspect.Parameter.KEYWORD_ONLY,
                                )}
                    kwargs = {k: v for k, v in kwargs.items() if k in accepted}
                return _cls(**kwargs)
            
            self._strategies[normalized_key] = factory
            return strategy_class  # return the original class, not factory
        return decorator

    def get(self, key: Union[str, Enum]) -> Optional[Callable[..., T]]:
        """Get a strategy factory by key.
        
        Args:
            key: Unique identifier for the strategy (string or enum).
            
        Returns:
            Strategy factory function, or None if not found.
        """
        normalized_key = self._normalize_key(key)
        return self._strategies.get(normalized_key)

    def create(self, key: Union[str, Enum], **kwargs: Any) -> T:
        """Create a strategy instance.
        
        Args:
            key: Unique identifier for the strategy (string or enum).
            **kwargs: Arguments passed to the strategy factory.
            
        Returns:
            Strategy instance.
            
        Raises:
            KeyError: If strategy key is not registered.
        """
        normalized_key = self._normalize_key(key)
        if normalized_key not in self._strategies:
            available = ", ".join(sorted(self._strategies.keys()))
            raise KeyError(
                f"Strategy '{normalized_key}' not found. "
                f"Available strategies: {available}"
            )
        factory = self._strategies[normalized_key]
        return factory(**kwargs)

    def registered_keys(self) -> list[str]:
        """Get all registered strategy keys.
        
        Returns:
            Sorted list of registered keys.
        """
        return sorted(self._strategies.keys())
