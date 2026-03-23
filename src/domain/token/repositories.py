"""
Интерфейс репозитория токенов.
"""

from abc import ABC, abstractmethod
from typing import List

from src.domain.token.filters import TokenFilters
from src.domain.token.models import Token


class TokenRepository(ABC):
    """
    Интерфейс репозитория токенов.

    Все реализации должны следовать этому интерфейсу.
    """

    @abstractmethod
    async def get(self, token_id: int) -> Token | None:
        """Получение токена по ID."""
        pass

    @abstractmethod
    async def get_by_token_value(self, token_value: str) -> Token | None:
        """
        Получение токена по значению.
        
        :param token_value: Значение токена
        :return: Токен или None
        """
        pass

    @abstractmethod
    async def list(self, limit: int = 100, offset: int = 0,
                   filters: TokenFilters | None = None) -> List[Token]:
        """
        Получение всех токенов с фильтрами.

        :param limit: Максимальное количество записей
        :param offset: Смещение (для пагинации)
        :param filters: Типизированные фильтры TokenFilters (опционально)
        :return: Список токенов
        """
        pass

    @abstractmethod
    async def create(self, token: Token) -> Token:
        """Создание токена."""
        pass

    @abstractmethod
    async def update(self, token: Token) -> Token:
        """Обновление токена."""
        pass

    @abstractmethod
    async def delete(self, token_id: int) -> None:
        """Удаление токена."""
        pass

    @abstractmethod
    async def count(self, filters: TokenFilters | None = None) -> int:
        """
        Подсчёт количества токенов.

        :param filters: Типизированные фильтры TokenFilters (опционально)
        :return: Количество токенов
        """
        pass
