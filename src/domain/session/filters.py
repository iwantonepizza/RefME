"""
Типизированные фильтры для сессий.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class SessionFilters:
    """
    Фильтры для поиска сессий.

    Все поля опциональны — используются только те, что переданы.
    """
    token_id: str | None = None  # Фильтр по ID токена
    chat_id: UUID | None = None  # Фильтр по ID чата
    created_after: datetime | None = None  # Созданы после даты
    created_before: datetime | None = None  # Созданы до даты
    is_deleted: bool | None = None  # Только удаленные/неудаленные
