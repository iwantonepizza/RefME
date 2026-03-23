"""
Тесты для утилит - увеличение покрытия.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient

from src.database.api_token import APIToken
from src.database.chat import ChatSettings
from src.database.llm_model import LLMModel


class TestEffectiveSettingsExtended:
    """Расширенные тесты для effective_settings."""

    @pytest.mark.asyncio
    async def test_get_effective_settings_with_full_model(
        self, test_chat: ChatSettings, test_model: LLMModel, test_db
    ):
        """Тест с полной моделью."""
        from src.infrastructure.utils.effective_settings import get_effective_settings
        
        # Устанавливаем все настройки модели
        test_model.temperature = 0.8
        test_model.max_tokens = 8192
        test_model.context_window = 16384
        test_chat.model = test_model
        test_chat.model_name = test_model.provider_model
        
        # Настройки чата None - должны взяться из модели
        test_chat.temperature = None
        test_chat.max_tokens = None
        test_chat.context_window = None
        
        result = get_effective_settings(test_chat)
        
        assert result["temperature"] == 0.8
        assert result["max_tokens"] == 8192
        assert result["context_window"] == 16384
        assert result["model"] == test_model.provider_model

    @pytest.mark.asyncio
    async def test_get_effective_settings_chat_overrides_model(
        self, test_chat: ChatSettings, test_model: LLMModel, test_db
    ):
        """Тест что настройки чата перекрывают модель."""
        from src.infrastructure.utils.effective_settings import get_effective_settings
        
        test_model.temperature = 0.5
        test_model.max_tokens = 2048
        test_chat.model = test_model
        test_chat.model_name = test_model.provider_model
        
        # Настройки чата отличаются от модели
        test_chat.temperature = 0.9
        test_chat.max_tokens = 4096
        
        result = get_effective_settings(test_chat)
        
        # Должны взяться из чата
        assert result["temperature"] == 0.9
        assert result["max_tokens"] == 4096

    @pytest.mark.asyncio
    async def test_get_effective_settings_no_model_no_chat_settings(
        self, test_chat: ChatSettings, test_db
    ):
        """Тест с отсутствующей моделью и настройками чата."""
        from src.infrastructure.utils.effective_settings import get_effective_settings
        
        test_chat.model = None
        test_chat.model_name = "fallback-model"
        test_chat.temperature = None
        test_chat.max_tokens = None
        test_chat.context_window = None
        
        result = get_effective_settings(test_chat)
        
        # Должны взяться дефолтные значения
        assert result["temperature"] == 0.7
        assert result["max_tokens"] == 4096
        assert result["context_window"] == 4096
        assert result["model"] == "fallback-model"


class TestApiTokensUtilsExtended:
    """Расширенные тесты для api_tokens утилит."""

    @pytest.mark.asyncio
    async def test_get_api_llm_token_from_headers_missing_header(
        self, client: AsyncClient
    ):
        """Тест отсутствия заголовка api-token."""
        # Тестируем через endpoint который использует get_llm_api_token_from_headers
        # POST /models/llm/ask требует api-token заголовок
        response = await client.post(
            "/models/llm/ask",
            data={"session_id": "00000000-0000-0000-0000-000000000000", "msg_text": "test"},
        )

        # Должен вернуть 401 или 422 из-за отсутствия токена
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_get_api_llm_token_from_headers_not_found(
        self, client: AsyncClient
    ):
        """Тест токена который не найден."""
        # Тестируем с несуществующим токеном
        response = await client.post(
            "/models/llm/ask",
            data={"session_id": "00000000-0000-0000-0000-000000000000", "msg_text": "test"},
            headers={"api-token": "nonexistent_token_12345"},
        )

        # Должен вернуть 401 из-за невалидного токена
        assert response.status_code == 401


class TestAuthUtilsExtended:
    """Расширенные тесты для auth утилит."""

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token_format(self):
        """Тест с невалидным форматом токена."""
        from src.infrastructure.utils.auth import get_current_user
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        # Передаём None вместо credentials
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=None)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_bearer_missing(self):
        """Тест с отсутствующим Bearer."""
        from src.infrastructure.utils.auth import get_current_user
        from fastapi import HTTPException

        # Передаём None вместо credentials — должен вернуть 401
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=None)

        assert exc_info.value.status_code == 401
        assert "Not authenticated" in str(exc_info.value.detail)


class TestImageHelpersExtended:
    """Расширенные тесты для image_helpers."""

    def test_encode_images_to_base64_empty_list(self):
        """Тест кодирования пустого списка изображений."""
        from src.infrastructure.utils.image_helpers import encode_images_to_base64
        
        result = encode_images_to_base64([])
        
        assert result == []


class TestRequestParsersExtended:
    """Расширенные тесты для request_parsers."""

    def test_parse_request_field_with_invalid_json(self):
        """Тест парсинга невалидного JSON."""
        from src.infrastructure.utils.request_parsers import parse_request_field
        
        # Невалидный JSON должен вернуться как строка
        result = parse_request_field("{invalid json}", "user")
        
        assert result.role == "user"

    def test_parse_request_field_with_json_missing_fields(self):
        """Тест парсинга JSON с отсутствующими полями."""
        from src.infrastructure.utils.request_parsers import parse_request_field
        import json
        
        data = {"msg": "Hello"}  # role отсутствует
        result = parse_request_field(json.dumps(data), None)
        
        assert result.msg == "Hello"

    def test_parse_request_field_with_json_extra_fields(self):
        """Тест парсинга JSON с лишними полями."""
        from src.infrastructure.utils.request_parsers import parse_request_field
        import json
        
        data = {"msg": "Hello", "role": "user", "extra_field": "ignored"}
        result = parse_request_field(json.dumps(data), None)
        
        assert result.msg == "Hello"
        assert result.role == "user"


class TestConstantsExtended:
    """Расширенные тесты для констант."""

    def test_max_prompt_length_from_settings(self):
        """Тест MAX_PROMPT_LENGTH из settings."""
        from src.core.config import settings

        assert settings.MAX_PROMPT_LENGTH == 32000
        assert isinstance(settings.MAX_PROMPT_LENGTH, int)
        assert settings.MAX_PROMPT_LENGTH > 0

    def test_max_image_size_mb_from_settings(self):
        """Тест MAX_IMAGE_SIZE_MB из settings."""
        from src.core.config import settings

        assert settings.MAX_IMAGE_SIZE_MB == 10
        assert isinstance(settings.MAX_IMAGE_SIZE_MB, int)
        assert settings.MAX_IMAGE_SIZE_MB > 0

    def test_max_images_per_request_from_settings(self):
        """Тест MAX_IMAGES_PER_REQUEST из settings."""
        from src.core.config import settings

        assert settings.MAX_IMAGES_PER_REQUEST == 5
        assert isinstance(settings.MAX_IMAGES_PER_REQUEST, int)
        assert settings.MAX_IMAGES_PER_REQUEST > 0

    def test_message_status_all_values(self):
        """Тест всех значений MessageStatus."""
        from src.core.constants import MessageStatus
        
        values = [status.value for status in MessageStatus]
        
        assert "pending" in values
        assert "processing" in values
        assert "completed" in values
        assert "failed" in values
        assert len(values) == 4

    def test_model_type_all_values(self):
        """Тест всех значений ModelType."""
        from src.core.constants import ModelType
        
        values = [status.value for status in ModelType]
        
        assert "text" in values
        assert "image" in values


class TestExceptionsExtended:
    """Расширенные тесты для исключений."""

    def test_token_not_found_error_message(self):
        """Тест сообщения об ошибке TokenNotFoundError."""
        from src.exceptions.exceptions import TokenNotFoundError
        
        error = TokenNotFoundError(123)
        
        assert "123" in str(error)
        assert "Токен" in str(error) or "Token" in str(error)

    def test_chat_not_found_error_message(self):
        """Тест сообщения об ошибке ChatNotFoundError."""
        from src.exceptions.exceptions import ChatNotFoundError
        from uuid import uuid4
        
        chat_id = uuid4()
        error = ChatNotFoundError(chat_id)
        
        assert str(chat_id) in str(error)

    def test_model_not_found_error_message(self):
        """Тест сообщения об ошибке ModelNotFoundError."""
        from src.exceptions.exceptions import ModelNotFoundError
        
        error = ModelNotFoundError(456)
        
        assert "456" in str(error)

    def test_session_not_found_error_message(self):
        """Тест сообщения об ошибке SessionNotFoundError."""
        from src.exceptions.exceptions import SessionNotFoundError
        from uuid import uuid4
        
        session_id = uuid4()
        error = SessionNotFoundError(session_id)
        
        assert str(session_id) in str(error)

    def test_model_inactive_error_message(self):
        """Тест сообщения об ошибке ModelInactiveError."""
        from src.exceptions.exceptions import ModelInactiveError
        
        error = ModelInactiveError("llama2")
        
        assert "llama2" in str(error)

    def test_llm_service_error_message(self):
        """Тест сообщения об ошибке LLMServiceError."""
        from src.exceptions.exceptions import LLMServiceError
        
        error = LLMServiceError("Provider unavailable")
        
        assert "Provider unavailable" in str(error)

    def test_invalid_token_error_message(self):
        """Тест сообщения об ошибке InvalidTokenError."""
        from src.exceptions.exceptions import InvalidTokenError
        
        error = InvalidTokenError("bad_token")
        
        assert "bad_token" in str(error)

    def test_model_already_exists_error(self):
        """Тест ModelAlreadyExistsError."""
        from src.exceptions.exceptions import ModelAlreadyExistsError
        
        error = ModelAlreadyExistsError("llama2:7b")
        
        assert "llama2:7b" in str(error)
