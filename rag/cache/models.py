"""Cache metadata model.

Every cache entry stores a ``metadata.json`` alongside its payload. The
``parent_cache_key`` field links each entry to the stage it derives from,
forming a cache lineage graph: chunk -> embedding -> index.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

CACHE_VERSION = "1.0"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CacheMetadata:
    """Metadata describing a single cache entry and its lineage."""

    cache_key: str
    cache_type: str  # "chunk" | "embedding" | "index"
    config_hash: str
    parent_cache_key: Optional[str] = None
    datasource_hash: Optional[str] = None
    created_at: str = field(default_factory=_utc_now)
    version: str = CACHE_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheMetadata":
        known = {f for f in cls.__dataclass_fields__}  # noqa: F841
        return cls(
            cache_key=data["cache_key"],
            cache_type=data["cache_type"],
            config_hash=data.get("config_hash", ""),
            parent_cache_key=data.get("parent_cache_key"),
            datasource_hash=data.get("datasource_hash"),
            created_at=data.get("created_at", _utc_now()),
            version=data.get("version", CACHE_VERSION),
        )
