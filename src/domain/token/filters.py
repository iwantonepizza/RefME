"""
Типизированные фильтры для токенов.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TokenFilters:
    """
    Фильтры для поиска токенов.

    Все поля опциональны — используются только те, что переданы.
    """
    active: bool | None = None  # Только активные/неактивные
    is_deleted: bool | None = None  # Только удаленные/неудаленные
    expires_before: datetime | None = None  # Истекают до даты
    expires_after: datetime | None = None  # Истекают после даты
    last_used_before: datetime | None = None  # Последнее использование до
    last_used_after: datetime | None = None  # Последнее использование после
