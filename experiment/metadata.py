"""Experiment metadata management.

Stores lightweight metadata separately from query results to enable
resume capability and experiment tracking.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class ExperimentStatus(str, Enum):
    """Status of an experiment run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ExperimentMetadata:
    """Metadata for an experiment run."""
    dataset: str
    config_name: str
    start_index: int
    end_index: Optional[int]
    total_queries: int
    created_at: str
    status: ExperimentStatus = ExperimentStatus.PENDING
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ExperimentMetadata':
        """Create from dictionary."""
        if isinstance(data.get('status'), str):
            data['status'] = ExperimentStatus(data['status'])
        return cls(**data)
    
    def save(self, path: Path):
        """Save metadata to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, path: Path) -> Optional['ExperimentMetadata']:
        """Load metadata from JSON file."""
        if not path.exists():
            return None
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def update_status(self, status: ExperimentStatus, error_message: Optional[str] = None):
        """Update experiment status."""
        self.status = status
        if status == ExperimentStatus.COMPLETED:
            self.completed_at = datetime.utcnow().isoformat()
        if error_message:
            self.error_message = error_message
