"""
Утилиты для работы с изображениями.
"""

import base64

from fastapi import HTTPException, UploadFile

from src.core.config import settings
from src.core.logging import logger


def encode_image_to_base64(file: UploadFile) -> str:
    """
    Кодирование загруженного файла в base64 строку с валидацией размера.

    :param file: Загруженный файл
    :return: Base64 строка изображения
    :raises HTTPException: Если файл слишком большой
    """
    # Проверяем размер файла через size атрибут
    file_size = file.size or 0

    max_size = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024  # Конвертируем в байты
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"Файл {file.filename} слишком большой. Максимальный размер: {settings.MAX_IMAGE_SIZE_MB}MB",
        )

    file_content = file.file.read()
    return base64.b64encode(file_content).decode("utf-8")


def encode_images_to_base64(images: list[UploadFile]) -> list[str]:
    """
    Кодирование списка изображений в base64.

    :param images: Список загруженных файлов
    :return: Список base64 строк
    :raises HTTPException: Если файл слишком большой или ошибка обработки
    """
    images_data = []

    for img in images:
        # Пропускаем пустые файлы
        if not img or img.size == 0:
            continue

        try:
            base64_img = encode_image_to_base64(img)
            images_data.append(base64_img)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка кодирования изображения {img.filename}: {e}")
            raise HTTPException(400, f"Ошибка обработки изображения: {img.filename}")

    return images_data
