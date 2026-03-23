"""Интерфейс для маршрутизации моделей."""

from abc import ABC, abstractmethod


class ModelRouter(ABC):
    """Интерфейс для маршрутизации моделей."""

    @abstractmethod
    async def get_provider(self, model_name: str) -> str | None:
        """Получение провайдера для модели."""
        pass

    @abstractmethod
    async def get_provider_for_model(self, model_name: str) -> object:
        """Получение провайдера для модели."""
        pass

    @abstractmethod
    async def get_fallback_provider(self, primary_provider: str) -> str | None:
        """Получение fallback провайдера."""
        pass

    @abstractmethod
    async def get_available_models(self, provider: str | None = None) -> list[str]:
        """Получение списка доступных моделей."""
        pass
