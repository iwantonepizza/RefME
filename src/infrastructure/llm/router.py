"""
Реализация Model Router.

Маршрутизация запросов к LLM провайдерам:
- Выбор провайдера по названию модели
- Fallback при ошибке
- Load balancing (round-robin)
"""

import logging
from typing import Dict, List

from src.core.config import settings
from src.domain.llm.router import ModelRouter
from src.infrastructure.llm.providers.factory import LLMProviderFactory, get_provider_factory

logger = logging.getLogger(__name__)


class LLMModelRouter(ModelRouter):
    """
    Реализация маршрутизации моделей.
    
    Логика:
    1. Если модель найдена в БД с указанным provider — используем его
    2. Иначе используем приоритет из конфига (LLM_PROVIDER_PRIORITY)
    3. При ошибке — fallback на следующий провайдер
    """

    def __init__(self, llm_factory: LLMProviderFactory):
        self.llm_factory = llm_factory
        self._provider_priority = settings.provider_priority_list
        self._model_provider_cache: dict[str, str] = {}

    async def get_provider(self, model_name: str) -> str | None:
        """
        Получение провайдера для модели.
        
        :param model_name: Название модели
        :return: Название провайдера или None
        """
        # Проверяем кеш
        if model_name in self._model_provider_cache:
            return self._model_provider_cache[model_name]

        # Проверяем доступность провайдеров по приоритету
        for provider_name in self._provider_priority:
            provider = self.llm_factory.get_provider(provider_name)
            if provider and await provider.health_check():
                # Проверяем есть ли такая модель у провайдера
                models = await provider.get_available_models()
                if model_name in models:
                    self._model_provider_cache[model_name] = provider_name
                    return provider_name

        logger.warning(f"No provider found for model: {model_name}")
        return None

    async def get_fallback_provider(self, primary_provider: str) -> str | None:
        """
        Получение fallback провайдера.
        
        :param primary_provider: Основной провайдер
        :return: Fallback провайдер или None
        """
        for provider_name in self._provider_priority:
            if provider_name != primary_provider:
                provider = self.llm_factory.get_provider(provider_name)
                if provider and await provider.health_check():
                    logger.info(f"Using fallback provider: {provider_name}")
                    return provider_name

        logger.error("No fallback provider available")
        return None

    async def get_available_models(self, provider: str | None = None) -> List[str]:
        """
        Получение списка доступных моделей.
        
        :param provider: Название провайдера (опционально)
        :return: Список названий моделей
        """
        if provider:
            provider_instance = self.llm_factory.get_provider(provider)
            if provider_instance:
                return await provider_instance.get_available_models()
            return []

        # Получаем модели от всех провайдеров
        all_models = set()
        for provider_name in self._provider_priority:
            provider_instance = self.llm_factory.get_provider(provider_name)
            if provider_instance:
                models = await provider_instance.get_available_models()
                all_models.update(models)

        return list(all_models)

    def clear_cache(self) -> None:
        """Очистка кеша маршрутизации."""
        self._model_provider_cache.clear()
        logger.info("Model router cache cleared")
