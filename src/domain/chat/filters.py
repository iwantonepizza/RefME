"""
Типизированные фильтры для чатов.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ChatFilters:
    """
    Фильтры для поиска чатов.

    Все поля опциональны — используются только те, что переданы.
    """
    model_id: int | None = None  # Фильтр по ID модели
    model_name: str | None = None  # Фильтр по названию модели
    token_id: int | None = None  # Фильтр по ID токена
    is_deleted: bool | None = None  # Только удаленные/неудаленные
