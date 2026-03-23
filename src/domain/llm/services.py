"""
Интерфейс для конфигурации LLM.

Domain layer не знает о config, только об интерфейсах.
"""

from abc import ABC, abstractmethod


class LLMConfigurationService(ABC):
    """
    Интерфейс для конфигурации LLM.

    Этот интерфейс используется в use cases для получения
    настроек без прямого импорта settings.
    """

    @abstractmethod
    async def get_max_images_per_request(self) -> int:
        """Получение максимального количества изображений на запрос."""
        pass

    @abstractmethod
    async def get_max_image_size_mb(self) -> int:
        """Получение максимального размера изображения в MB."""
        pass

    @abstractmethod
    async def get_max_prompt_length(self) -> int:
        """Получение максимальной длины промпта."""
        pass
