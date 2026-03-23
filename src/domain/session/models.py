"""
Domain модель сессии.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Session:
    """Бизнес-объект сессии."""
    token_id: str
    session_id: UUID = field(default_factory=uuid4)
    chat_id: UUID = field(default_factory=uuid4)
    created_at: datetime | None = None
    deleted_at: datetime | None = None
