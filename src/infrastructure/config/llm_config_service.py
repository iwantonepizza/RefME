"""
Реализация сервиса конфигурации LLM.

Infrastructure layer знает и о settings, и о domain интерфейсах.
"""

from src.core.config import Settings
from src.domain.llm.services import LLMConfigurationService


class LLMConfigService(LLMConfigurationService):
    """
    Реализация сервиса конфигурации LLM.

    Использует Settings для получения значений.
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    async def get_max_images_per_request(self) -> int:
        """Получение максимального количества изображений на запрос."""
        return self.settings.MAX_IMAGES_PER_REQUEST

    async def get_max_image_size_mb(self) -> int:
        """Получение максимального размера изображения в MB."""
        return self.settings.MAX_IMAGE_SIZE_MB

    async def get_max_prompt_length(self) -> int:
        """Получение максимальной длины промпта."""
        return self.settings.MAX_PROMPT_LENGTH
