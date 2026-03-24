"""
Domain модель сообщения.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.core.constants import MessageStatus, Role


@dataclass
class Message:
    """Бизнес-объект сообщения."""
    role: Role
    content: str
    status: MessageStatus
    message_id: UUID = field(default_factory=uuid4)
    session_id: UUID = field(default_factory=uuid4)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    deleted_at: datetime | None = None

    def __post_init__(self):
        """Валидация при создании сообщения."""
        if not self.content or not self.content.strip():
            raise ValueError("Message content required")

        if len(self.content) > 32000:
            raise ValueError("Message content too long (max 32000 chars)")

        self.content = self.content.strip()
