"""
Фабрика для создания и выбора LLM провайдеров.
"""

from typing import Dict, List, Optional

from src.core.config import settings
from src.domain.llm_model.repositories import ModelRepositoryInterface
from src.exceptions.exceptions import LLMServiceError
from src.core.logging import logger
from src.infrastructure.llm.providers.base import LLMProvider
from src.infrastructure.llm.providers.ollama import OllamaProvider
from src.infrastructure.llm.providers.vllm import VLLMProvider


class LLMProviderFactory:
    """
    Фабрика для управления LLM провайдерами.

    Логика выбора провайдера:
    1. Если у модели указан provider в БД - используем его
    2. Иначе используем приоритет из конфига (LLM_PROVIDER_PRIORITY)
    3. Проверяем health провайдера перед использованием
    """

    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Инициализация доступных провайдеров."""
        # Всегда регистрируем Ollama
        self.register("ollama", OllamaProvider(settings.OLLAMA_URL, max_retries=3, base_delay=1.0))
        logger.info("Ollama provider registered with retry support")

        # Регистрируем vLLM если настроен
        if settings.VLLM_URL:
            self.register("vllm", VLLMProvider(settings.VLLM_URL, settings.VLLM_API_KEY))
            logger.info(f"vLLM provider registered: {settings.VLLM_URL}")
        else:
            logger.info("vLLM not configured (VLLM_URL not set)")

    def register(self, name: str, provider: LLMProvider) -> None:
        """
        Регистрация провайдера.

        :param name: Название провайдера
        :param provider: Экземпляр провайдера
        """
        self._providers[name] = provider
        logger.debug(f"Provider '{name}' registered")

    def unregister(self, name: str) -> None:
        """
        Удаление провайдера.

        :param name: Название провайдера
        """
        if name in self._providers:
            del self._providers[name]
            logger.debug(f"Provider '{name}' unregistered")

    def get_provider(self, name: str) -> LLMProvider | None:
        """
        Получение провайдера по названию.

        :param name: Название провайдера
        :return: Провайдер или None
        """
        return self._providers.get(name)

    def get_all_providers(self) -> List[str]:
        """
        Получение списка всех зарегистрированных провайдеров.

        :return: Список названий провайдеров
        """
        return list(self._providers.keys())

    async def get_provider_for_model(
        self,
        model_name: str,
        model_repository: ModelRepositoryInterface | None = None
    ) -> LLMProvider:
        """
        Выбор провайдера для модели.

        Логика:
        1. Проверяем provider в БД (model.provider)
        2. Если не указано, используем priority из конфига
        3. Проверяем health провайдера

        :param model_name: Название модели
        :param model_repository: Репозиторий моделей (опционально)
        :return: Провайдер для модели
        :raises LLMServiceError: Если нет доступного провайдера
        """
        provider_name = None

        # Пытаемся получить модель из БД
        if model_repository:
            model = await model_repository.get_by_provider_model(model_name)
            if model and model.provider:
                provider_name = model.provider
                logger.info(f"Using provider '{provider_name}' from database for model '{model_name}'")

        # Если provider не указан в БД, используем priority
        if not provider_name:
            provider_name = await self._get_provider_by_priority(model_name)
            if provider_name:
                logger.info(f"Using provider '{provider_name}' by priority for model '{model_name}'")

        # Если всё ещё нет, пробуем все доступные
        if not provider_name:
            provider_name = await self._get_any_healthy_provider()

        if not provider_name:
            raise LLMServiceError("No available LLM provider")

        provider = self._providers.get(provider_name)
        if not provider:
            raise LLMServiceError(f"Provider '{provider_name}' not found")

        return provider

    async def _get_provider_by_priority(self, model_name: str) -> str | None:
        """Получение провайдера по приоритету из конфига."""
        for provider_name in settings.provider_priority_list:
            if provider_name in self._providers:
                provider = self._providers[provider_name]
                if await provider.health_check():
                    return provider_name

        return None

    async def _get_any_healthy_provider(self) -> str | None:
        """Получение любого здорового провайдера."""
        for name, provider in self._providers.items():
            if await provider.health_check():
                return name
        return None

    async def health_check_all(self) -> Dict[str, bool]:
        """
        Проверка здоровья всех провайдеров.

        :return: Словарь {provider_name: is_healthy}
        """
        results = {}
        for name, provider in self._providers.items():
            results[name] = await provider.health_check()
        return results

    async def get_all_available_models(self) -> Dict[str, List[str]]:
        """
        Получение списков моделей от всех провайдеров.

        :return: Словарь {provider_name: [models]}
        """
        results = {}
        for name, provider in self._providers.items():
            results[name] = await provider.get_available_models()
        return results


# Глобальный экземпляр фабрики
_factory: LLMProviderFactory | None = None


def get_provider_factory() -> LLMProviderFactory:
    """Получение глобального экземпляра фабрики."""
    global _factory
    if _factory is None:
        _factory = LLMProviderFactory()
    return _factory


def reset_provider_factory() -> None:
    """Сброс фабрики (для тестов)."""
    global _factory
    _factory = None
