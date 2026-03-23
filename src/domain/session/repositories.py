"""
Интерфейс репозитория сессий.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.session.filters import SessionFilters
from src.domain.session.models import Session


class SessionRepository(ABC):
    """Интерфейс репозитория сессий."""

    @abstractmethod
    async def get(self, session_id: UUID) -> Session | None:
        """Получение сессии по ID."""
        pass

    @abstractmethod
    async def get_by_token_id_and_session_id(
        self, token_id: str, session_id: UUID
    ) -> Session | None:
        """
        Получение сессии по token_id и session_id.

        :param token_id: Значение токена (не ID!)
        :param session_id: UUID сессии
        :return: Сессия или None

        Примечание: Этот метод используется для проверки принадлежности сессии токену.
        Возвращает сессию только если она принадлежит указанному токену.
        """
        pass

    @abstractmethod
    async def list(self, token_id: str, limit: int = 100, offset: int = 0,
                   filters: SessionFilters | None = None) -> List[Session]:
        """
        Получение сессий по token_id с фильтрами.

        :param token_id: Значение токена
        :param limit: Максимальное количество записей
        :param offset: Смещение (для пагинации)
        :param filters: Типизированные фильтры SessionFilters (опционально)
        :return: Список сессий
        """
        pass

    @abstractmethod
    async def get_by_chat_id(self, chat_id: UUID) -> List[Session]:
        """Получение сессий по chat_id."""
        pass

    @abstractmethod
    async def create(self, session: Session) -> Session:
        """Создание сессии."""
        pass

    @abstractmethod
    async def update(self, session: Session) -> Session:
        """Обновление сессии."""
        pass

    @abstractmethod
    async def delete(self, session_id: UUID) -> None:
        """Удаление сессии."""
        pass

    @abstractmethod
    async def count(self, filters: SessionFilters | None = None) -> int:
        """
        Подсчёт количества сессий.

        :param filters: Типизированные фильтры SessionFilters (опционально)
        :return: Количество сессий
        """
        pass
