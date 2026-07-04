"""Provider configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from providers.enums import ProviderType


@dataclass
class BaseProviderConfig:
    """Base class for all provider strategy configurations."""
    pass


@dataclass
class ProviderConfig:
    """Provider section: which strategy plus its own typed config."""
    type: ProviderType
    api_key_env: Optional[str] = None
    params: dict = None

    def __post_init__(self):
        self.type = ProviderType(self.type)
        if self.params is None:
            self.params = {}
