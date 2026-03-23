"""
Типизированные фильтры для сообщений.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MessageFilters:
    """
    Фильтры для поиска сообщений.

    Все поля опциональны — используются только те, что переданы.
    """
    session_id: str | None = None  # Фильтр по ID сессии
    role: str | None = None  # Фильтр по роли (user/assistant/system)
    status: str | None = None  # Фильтр по статусу
    created_after: datetime | None = None  # Созданы после даты
    created_before: datetime | None = None  # Созданы до даты
    is_deleted: bool | None = None  # Только удаленные/неудаленные
