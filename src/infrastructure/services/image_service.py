"""
Сервис для работы с изображениями.

Инкапсулирует логику:
- Кодирования изображений в base64
- Валидации количества и размера изображений
"""

from typing import List

from fastapi import UploadFile

from src.core.config import settings
from src.exceptions.domain_exceptions import TooManyImagesError


class ImageService:
    """Сервис для обработки изображений."""

    @staticmethod
    def validate_images_count(images: List[UploadFile | None] | None) -> None:
        """
        Валидация количества изображений.

        :param images: Список изображений
        :raises TooManyImagesError: Если изображений больше максимума
        """
        if not images:
            return

        # Фильтруем None значения
        valid_images = [img for img in images if img is not None]
        max_images = settings.MAX_IMAGES_PER_REQUEST

        if len(valid_images) > max_images:
            raise TooManyImagesError(max_images)

    @staticmethod
    async def encode_images(images: List[UploadFile | None] | None) -> List[str] | None:
        """
        Кодирование изображений в base64.

        :param images: Список изображений
        :return: Список base64 строк или None
        """
        if not images:
            return None

        # Фильтруем None значения
        valid_images = [img for img in images if img is not None]
        if not valid_images:
            return None

        # Импортируем утилиту кодирования
        from src.infrastructure.utils.image_helpers import encode_images_to_base64
        return encode_images_to_base64(valid_images)

    @staticmethod
    async def process_images(
        images: List[UploadFile | None] | None
    ) -> List[str] | None:
        """
        Полная обработка изображений: валидация + кодирование.

        :param images: Список изображений
        :return: Список base64 строк или None
        :raises TooManyImagesError: Если изображений больше максимума
        """
        ImageService.validate_images_count(images)
        return await ImageService.encode_images(images)
