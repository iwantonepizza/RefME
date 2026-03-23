"""
Интерфейс репозитория чатов.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.chat.filters import ChatFilters
from src.domain.chat.models import Chat


class ChatRepository(ABC):
    """Интерфейс репозитория чатов."""

    @abstractmethod
    async def get(self, chat_id: UUID) -> Chat | None:
        """Получение чата по ID."""
        pass

    @abstractmethod
    async def get_by_token_id_and_chat_id(self, token_id: int, chat_id: UUID) -> Chat | None:
        """Получение чата по token_id и chat_id."""
        pass

    @abstractmethod
    async def list(self, token_id: int, limit: int = 100, offset: int = 0,
                   filters: ChatFilters | None = None) -> List[Chat]:
        """
        Получение списка чатов с фильтрами.

        :param token_id: ID токена владельца
        :param limit: Максимальное количество записей
        :param offset: Смещение (для пагинации)
        :param filters: Типизированные фильтры ChatFilters (опционально)
        :return: Список чатов
        """
        pass

    @abstractmethod
    async def create(self, chat: Chat) -> Chat:
        """Создание чата."""
        pass

    @abstractmethod
    async def update(self, chat: Chat) -> Chat:
        """Обновление чата."""
        pass

    @abstractmethod
    async def delete(self, chat_id: UUID) -> None:
        """Удаление чата."""
        pass

    @abstractmethod
    async def count(self, filters: ChatFilters | None = None) -> int:
        """
        Подсчёт количества чатов.

        :param filters: Типизированные фильтры ChatFilters (опционально)
        :return: Количество чатов
        """
        pass

    @abstractmethod
    async def count_sessions(self, chat_id: UUID) -> int:
        """Подсчёт количества сессий у чата."""
        pass
