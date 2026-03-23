"""Базовый класс для domain событий."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class DomainEvent:
    """Базовый класс для всех domain событий."""
    event_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = field(init=False)

    def __post_init__(self):
        """Установка типа события из имени класса."""
        if not hasattr(self, 'event_type') or not self.event_type:
            self.event_type = self.__class__.__name__
