"""
Тесты для domain модели Chat.
"""

import pytest
from uuid import UUID
from datetime import datetime, timezone

from src.domain.chat.models import Chat


class TestChatModel:
    """Тесты для Chat domain модели."""

    def test_chat_create_valid(self):
        """Создание валидного чата."""
        chat = Chat(
            token_id=1,
            name="Test Chat",
            temperature=0.7,
            max_tokens=4096,
            context_window=8192
        )
        
        assert chat.token_id == 1
        assert chat.name == "Test Chat"
        assert chat.temperature == 0.7
        assert chat.max_tokens == 4096
        assert chat.context_window == 8192
        assert isinstance(chat.chat_id, UUID)

    def test_chat_name_too_long(self):
        """Проверка валидации длины названия."""
        with pytest.raises(ValueError) as exc_info:
            Chat(
                token_id=1,
                name="x" * 101  # Больше 100 символов
            )
        assert "Chat name too long" in str(exc_info.value)

    def test_system_prompt_too_long(self):
        """Проверка валидации длины системного промпта."""
        with pytest.raises(ValueError) as exc_info:
            Chat(
                token_id=1,
                system_prompt="x" * 32001  # Больше 32000 символов
            )
        assert "System prompt too long" in str(exc_info.value)

    def test_temperature_invalid_low(self):
        """Проверка валидации температуры (слишком низкая)."""
        with pytest.raises(ValueError) as exc_info:
            Chat(
                token_id=1,
                temperature=-0.1
            )
        assert "Temperature must be 0.0-2.0" in str(exc_info.value)

    def test_temperature_invalid_high(self):
        """Проверка валидации температуры (слишком высокая)."""
        with pytest.raises(ValueError) as exc_info:
            Chat(
                token_id=1,
                temperature=2.1
            )
        assert "Temperature must be 0.0-2.0" in str(exc_info.value)

    def test_max_tokens_invalid(self):
        """Проверка валидации max_tokens."""
        with pytest.raises(ValueError) as exc_info:
            Chat(
                token_id=1,
                max_tokens=-1  # Отрицательное значение
            )
        assert "max_tokens must be 1-32768" in str(exc_info.value)

    def test_context_window_invalid(self):
        """Проверка валидации context_window."""
        with pytest.raises(ValueError) as exc_info:
            Chat(
                token_id=1,
                context_window=100
            )
        assert "context_window must be 512-131072" in str(exc_info.value)

    def test_chat_defaults(self):
        """Проверка значений по умолчанию."""
        chat = Chat(token_id=1)
        
        assert chat.name is None
        assert chat.system_prompt is None
        assert chat.temperature is None
        assert chat.max_tokens is None
        assert chat.context_window is None
        assert chat.created_at is None
