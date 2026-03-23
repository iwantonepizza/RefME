"""
Интерфейс репозитория сообщений.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from uuid import UUID

from src.domain.message.filters import MessageFilters
from src.domain.message.models import Message


class MessageRepository(ABC):
    """Интерфейс репозитория сообщений."""

    @abstractmethod
    async def get(self, message_id: UUID) -> Message | None:
        """Получение сообщения по ID."""
        pass

    @abstractmethod
    async def list(self, session_id: UUID, limit: int = 100, offset: int = 0,
                   filters: MessageFilters | None = None) -> List[Message]:
        """
        Получение сообщений по session_id с фильтрами.

        :param session_id: UUID сессии
        :param limit: Максимальное количество записей
        :param offset: Смещение (для пагинации)
        :param filters: Типизированные фильтры MessageFilters (опционально)
        :return: Список сообщений
        """
        pass

    @abstractmethod
    async def create(self, message: Message) -> Message:
        """Создание сообщения."""
        pass

    @abstractmethod
    async def delete(self, message_id: UUID) -> None:
        """Удаление сообщения."""
        pass

    @abstractmethod
    async def count(self, filters: MessageFilters | None = None) -> int:
        """
        Подсчёт количества сообщений.

        :param filters: Типизированные фильтры MessageFilters (опционально)
        :return: Количество сообщений
        """
        pass

    @abstractmethod
    async def get_last_message_timestamp(self, session_id: UUID) -> datetime | None:
        """Получение времени последнего сообщения в сессии."""
        pass

    @abstractmethod
    async def count_messages(self, session_id: UUID) -> int:
        """Подсчёт количества сообщений в сессии."""
        pass

    @abstractmethod
    async def get_last_n_messages(self, session_id: UUID, n: int) -> List[Message]:
        """Получение последних n сообщений."""
        pass
