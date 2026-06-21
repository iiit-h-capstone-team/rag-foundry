from dataclasses import dataclass
from datetime import datetime


@dataclass
class KeyState:
    api_key: str
    cooldown_until: datetime | None = None

    total_requests: int = 0
    total_successes: int = 0
    total_failures: int = 0
    total_429s: int = 0

    @property
    def available(self) -> bool:
        if self.cooldown_until is None:
            return True

        return datetime.now() >= self.cooldown_until