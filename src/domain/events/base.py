"""Базовый класс для domain событий."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class EventType(StrEnum):
    """Типы domain событий."""
    # Chat events
    CHAT_CREATED = "chat_created"
    CHAT_UPDATED = "chat_updated"
    CHAT_DELETED = "chat_deleted"
    
    # Session events
    SESSION_CREATED = "session_created"
    SESSION_UPDATED = "session_updated"
    SESSION_DELETED = "session_deleted"
    
    # Token events
    TOKEN_CREATED = "token_created"
    TOKEN_UPDATED = "token_updated"
    TOKEN_DELETED = "token_deleted"
    TOKEN_VALIDATED = "token_validated"


@dataclass
class DomainEvent:
    """Базовый класс для всех domain событий."""
    event_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)  # Время создания события
    event_type: EventType = field(init=False)

    def __post_init__(self):
        """Установка типа события из имени класса."""
        if not hasattr(self, 'event_type') or not self.event_type:
            class_name = self.__class__.__name__
            # Конвертируем имя класса в EventType (например, ChatCreated -> CHAT_CREATED)
            import re
            event_type_str = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
            self.event_type = EventType(event_type_str)
