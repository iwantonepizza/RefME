"""
Domain события для сессий.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any
from uuid import UUID, uuid4

from src.domain.events.base import DomainEvent


@dataclass
class SessionCreated(DomainEvent):
    """Событие: сессия создана."""
    token_id: str = ""
    session_id: UUID = field(default_factory=uuid4)
    chat_id: UUID = field(default_factory=uuid4)


@dataclass
class SessionDeleted(DomainEvent):
    """Событие: сессия удалена."""
    token_id: str = ""
    session_id: UUID = field(default_factory=uuid4)


@dataclass
class SessionReassigned(DomainEvent):
    """Событие: сессия перепривязана к другому чату."""
    session_id: UUID = field(default_factory=uuid4)
    old_chat_id: UUID = field(default_factory=uuid4)
    new_chat_id: UUID = field(default_factory=uuid4)
