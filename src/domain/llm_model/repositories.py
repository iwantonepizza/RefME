"""
Интерфейс репозитория для LLM моделей.
"""

from abc import ABC, abstractmethod
from typing import List

from src.domain.llm_model.models import LLMModel


class ModelRepositoryInterface(ABC):
    """
    Интерфейс репозитория для LLM моделей.

    Все реализации должны следовать этому интерфейсу.
    """

    @abstractmethod
    async def get_by_id(self, model_id: int) -> LLMModel | None:
        """Получение модели по ID."""
        pass

    @abstractmethod
    async def get_by_provider_model(self, provider_model: str) -> LLMModel | None:
        """Получение модели по provider_model."""
        pass

    @abstractmethod
    async def list(self, active_only: bool = True, limit: int | None = None,
                   offset: int | None = None, filters: dict | None = None) -> List[LLMModel]:
        """Получение всех моделей с фильтрами."""
        pass

    @abstractmethod
    async def get_active_models(self) -> List[LLMModel]:
        """Получение всех активных моделей."""
        pass

    @abstractmethod
    async def create(self, model: LLMModel) -> LLMModel:
        """Создание модели."""
        pass

    @abstractmethod
    async def update(self, model: LLMModel) -> LLMModel:
        """Обновление модели."""
        pass

    @abstractmethod
    async def delete(self, model_id: int) -> None:
        """Удаление модели."""
        pass

    @abstractmethod
    async def count(self, filters: dict | None = None) -> int:
        """Подсчёт количества моделей."""
        pass

    @abstractmethod
    async def count_chats(self, model_id: int) -> int:
        """Подсчёт количества чатов у модели."""
        pass
