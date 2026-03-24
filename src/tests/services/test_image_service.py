"""
Тесты для ImageService.
"""

import pytest
from unittest.mock import Mock

from src.infrastructure.services.image_service import ImageService
from src.exceptions.domain_exceptions import TooManyImagesError


class TestImageService:
    """Тесты для ImageService."""

    def test_validate_images_count_none(self):
        """Валидация None списка."""
        # Не должно вызывать исключений
        ImageService.validate_images_count(None)

    def test_validate_images_count_empty(self):
        """Валидация пустого списка."""
        ImageService.validate_images_count([])

    def test_validate_images_count_valid(self):
        """Валидация допустимого количества."""
        mock_images = [Mock() for _ in range(3)]
        ImageService.validate_images_count(mock_images)

    def test_validate_images_count_exceeds(self):
        """Валидация превышения лимита."""
        mock_images = [Mock() for _ in range(10)]  # Больше MAX_IMAGES_PER_REQUEST (5)
        
        with pytest.raises(TooManyImagesError) as exc_info:
            ImageService.validate_images_count(mock_images)
        
        assert "Максимум: 5 изображений" in str(exc_info.value)

    def test_validate_images_count_with_none_values(self):
        """Валидация списка с None значениями."""
        mock_images = [Mock(), None, Mock(), None, Mock(), None, Mock()]
        # 4 валидных изображения — должно пройти
        ImageService.validate_images_count(mock_images)

    def test_validate_images_count_with_none_values_exceeds(self):
        """Валидация списка с None значениями (превышение)."""
        mock_images = [Mock() for _ in range(6)] + [None, None]
        # 6 валидных изображений — превышение
        
        with pytest.raises(TooManyImagesError):
            ImageService.validate_images_count(mock_images)
