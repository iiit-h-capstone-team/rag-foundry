"""Deterministic hashing utilities for cache keys.

All hashes are content-based and stable across processes: they are derived from
document contents and serialized config values, never from object identities or
memory addresses.
"""

import hashlib
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any, Iterable


def sha256_hex(data: Any) -> str:
    """SHA-256 hex digest of ``str`` or ``bytes`` input."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _json_default(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)
    raise TypeError(f"Cannot serialize {type(obj)!r} for hashing")


def serialize_config(config: Any) -> str:
    """Serialize a config object/dict to a stable JSON string.

    Dataclasses are expanded recursively and keys are sorted, so two equivalent
    configs always produce the same string regardless of field declaration order.
    """
    if is_dataclass(config) and not isinstance(config, type):
        payload: Any = asdict(config)
    else:
        payload = config
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=_json_default,
    )


def hash_config(config: Any) -> str:
    """Deterministic SHA-256 of a config section's serialized contents."""
    return sha256_hex(serialize_config(config))


def hash_documents(documents: Iterable[Any]) -> str:
    """Content-based, deterministic hash of a datasource.

    Derived from the concatenated ``title`` + ``content`` of every document in
    order. Two datasets with identical contents hash identically; any change to
    document text changes the hash.
    """
    hasher = hashlib.sha256()
    for doc in documents:
        title = getattr(doc, "title", "") or ""
        content = getattr(doc, "content", "") or ""
        hasher.update(title.encode("utf-8"))
        hasher.update(b"\x1f")  # unit separator between title and content
        hasher.update(content.encode("utf-8"))
        hasher.update(b"\x1e")  # record separator between documents
    return hasher.hexdigest()


def combine_keys(*parts: str) -> str:
    """Combine parent key + config hash into a child cache key.

    The lineage is encoded directly: a child key changes whenever either the
    parent key or the stage config changes.
    """
    return sha256_hex("|".join(parts))
