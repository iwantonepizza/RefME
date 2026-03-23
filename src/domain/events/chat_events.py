"""
Domain события для чатов.
"""

from dataclasses import dataclass, field
from uuid import UUID

from src.domain.events.base import DomainEvent


@dataclass
class ChatCreated(DomainEvent):
    """Событие: чат создан."""
    chat_id: UUID = field(default_factory=uuid4)
    token_id: int
    name: str | None = None


@dataclass
class ChatUpdated(DomainEvent):
    """Событие: чат обновлён."""
    chat_id: UUID = field(default_factory=uuid4)
    token_id: int
    updated_fields: dict[str, object] = field(default_factory=dict)


@dataclass
class ChatDeleted(DomainEvent):
    """Событие: чат удалён."""
    chat_id: UUID = field(default_factory=uuid4)
    token_id: int
