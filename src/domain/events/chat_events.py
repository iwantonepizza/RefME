"""
Domain события для чатов.
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.domain.events.base import DomainEvent


@dataclass
class ChatCreated(DomainEvent):
    """Событие: чат создан."""
    token_id: int = 0
    chat_id: UUID = field(default_factory=uuid4)
    name: str | None = None


@dataclass
class ChatUpdated(DomainEvent):
    """Событие: чат обновлён."""
    token_id: int = 0
    chat_id: UUID = field(default_factory=uuid4)
    updated_fields: dict[str, object] = field(default_factory=dict)


@dataclass
class ChatDeleted(DomainEvent):
    """Событие: чат удалён."""
    token_id: int = 0
    chat_id: UUID = field(default_factory=uuid4)
