"""
Универсальные результаты для CRUD операций.

Используются в domain слое для консистентного API пагинации.
"""

from dataclasses import dataclass
from typing import Generic, List, TypeVar

T = TypeVar('T')


@dataclass
class ListResult(Generic[T]):
    """
    Универсальный результат пагинированного списка.
    
    Используется в use cases для возврата списков с мета-данными.
    
    :param items: Список элементов
    :param total: Общее количество элементов (для пагинации)
    :param limit: Лимит (максимальное количество возвращаемых элементов)
    :param offset: Смещение (для пагинации)
    """
    items: List[T]
    total: int
    limit: int
    offset: int
    
    @property
    def has_more(self) -> bool:
        """Есть ли ещё элементы для загрузки."""
        return (self.offset + self.limit) < self.total
    
    @property
    def page_count(self) -> int:
        """Количество страниц."""
        return (self.total + self.limit - 1) // self.limit


@dataclass
class DeleteResult:
    """
    Результат операции удаления.
    """
    success: bool = True
    message: str = "Entity deleted"


@dataclass
class OperationResult:
    """
    Результат операции (универсальный).
    """
    success: bool
    message: str | None = None
    data: dict | None = None
