"""
Domain события для токенов.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.domain.events.base import DomainEvent


@dataclass
class TokenCreated(DomainEvent):
    """Событие: токен создан."""
    token_id: int = 0
    expires_at: datetime | None = None


@dataclass
class TokenUpdated(DomainEvent):
    """Событие: токен обновлён."""
    token_id: int = 0
    updated_fields: dict[str, object] = field(default_factory=dict)


@dataclass
class TokenDeleted(DomainEvent):
    """Событие: токен удалён."""
    token_id: int = 0


@dataclass
class TokenValidated(DomainEvent):
    """Событие: токен валидирован."""
    token_id: int = 0
    is_valid: bool = False
