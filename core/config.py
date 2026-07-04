"""Configuration helper utilities."""

from typing import Any, TypeVar, Type
from dataclasses import is_dataclass

T = TypeVar("T")


def coerce_config(value: Any, config_cls: Type[T]) -> T:
    """Convert a value into a typed config instance.
    
    Accepts None (use defaults), a plain dict (from JSON/YAML), or an
    already-built config object. Returns the appropriate instance.
    
    Args:
        value: None, dict, or dataclass instance.
        config_cls: Target dataclass type.
        
    Returns:
        Instance of config_cls.
        
    Raises:
        TypeError: If value is not None, dict, or dataclass instance.
    """
    if value is None:
        return config_cls()
    if isinstance(value, dict):
        return config_cls(**value)
    if is_dataclass(value) and isinstance(value, config_cls):
        return value
    return value
