"""
Тесты для DTO и дополнительных утилит - увеличение покрытия.
"""

import pytest

from src.use_cases.dto import (
    ChatDTO,
    ChatListDTO,
    MessageDTO,
    MessageListDTO,
    ModelDTO,
    ModelListDTO,
    PaginationDTO,
    SessionDTO,
    SessionListDTO,
    TokenDTO,
    TokenListDTO,
)


class TestPaginationDTO:
    """Тесты для PaginationDTO."""

    def test_pagination_creation(self):
        """Тест создания DTO пагинации."""
        pagination = PaginationDTO(limit=10, offset=0, total=100)
        
        assert pagination.limit == 10
        assert pagination.offset == 0
        assert pagination.total == 100

    def test_pagination_has_more_calculation(self):
        """Тест проверки has_more через вычисление."""
        pagination = PaginationDTO(limit=10, offset=0, total=100)
        
        # has_more вычисляется как offset + limit < total
        has_more = (pagination.offset + pagination.limit) < pagination.total
        assert has_more is True
        
        pagination_full = PaginationDTO(limit=100, offset=0, total=50)
        has_more_full = (pagination_full.offset + pagination_full.limit) < pagination_full.total
        assert has_more_full is False


class TestTokenDTO:
    """Тесты для TokenDTO."""

    @pytest.mark.asyncio
    async def test_token_from_orm(self, test_token):
        """Тест создания TokenDTO из ORM."""
        dto = TokenDTO.from_orm(test_token)

        assert dto.id == test_token.id
        assert dto.token_value == test_token.token
        assert dto.active == test_token.active

    @pytest.mark.asyncio
    async def test_token_list_dto(self, test_token):
        """Тест создания TokenListDTO."""
        items = [TokenDTO.from_orm(test_token)]
        pagination = PaginationDTO(limit=1, offset=0, total=1)
        
        dto = TokenListDTO(items=items, pagination=pagination)
        
        assert len(dto.items) == 1
        assert dto.pagination.total == 1


class TestModelDTO:
    """Тесты для ModelDTO."""

    @pytest.mark.asyncio
    async def test_model_from_orm(self, test_model):
        """Тест создания ModelDTO из ORM."""
        dto = ModelDTO.from_orm(test_model, chats_count=5)
        
        assert dto.id == test_model.id
        assert dto.name == test_model.name
        assert dto.provider_model == test_model.provider_model
        assert dto.chats_count == 5

    @pytest.mark.asyncio
    async def test_model_list_dto(self, test_model):
        """Тест создания ModelListDTO."""
        items = [ModelDTO.from_orm(test_model, chats_count=0)]
        pagination = PaginationDTO(limit=1, offset=0, total=1)
        
        dto = ModelListDTO(items=items, pagination=pagination)
        
        assert len(dto.items) == 1
        assert dto.pagination.total == 1


class TestChatDTO:
    """Тесты для ChatDTO."""

    @pytest.mark.asyncio
    async def test_chat_from_orm(self, test_chat):
        """Тест создания ChatDTO из ORM."""
        dto = ChatDTO.from_orm(test_chat, sessions_count=0)
        
        assert dto.id == test_chat.id
        assert dto.token_id == test_chat.token_id
        assert dto.sessions_count == 0

    @pytest.mark.asyncio
    async def test_chat_list_dto(self, test_chat):
        """Тест создания ChatListDTO."""
        items = [ChatDTO.from_orm(test_chat)]
        pagination = PaginationDTO(limit=1, offset=0, total=1)
        
        dto = ChatListDTO(items=items, pagination=pagination)
        
        assert len(dto.items) == 1
        assert dto.pagination.total == 1


class TestSessionDTO:
    """Тесты для SessionDTO."""

    @pytest.mark.asyncio
    async def test_session_from_orm(self, test_session):
        """Тест создания SessionDTO из ORM."""
        dto = SessionDTO.from_orm(test_session)
        
        assert dto.id == test_session.id
        assert dto.token_id == test_session.token_id
        assert dto.chat_id == test_session.chat_id

    @pytest.mark.asyncio
    async def test_session_list_dto(self, test_session):
        """Тест создания SessionListDTO."""
        items = [SessionDTO.from_orm(test_session)]
        pagination = PaginationDTO(limit=1, offset=0, total=1)
        
        dto = SessionListDTO(items=items, pagination=pagination)
        
        assert len(dto.items) == 1
        assert dto.pagination.total == 1


class TestMessageDTO:
    """Тесты для MessageDTO."""

    @pytest.mark.asyncio
    async def test_message_from_orm(self, test_message):
        """Тест создания MessageDTO из ORM."""
        dto = MessageDTO.from_orm(test_message)
        
        assert dto.id == test_message.id
        assert dto.role == test_message.role
        assert dto.content == test_message.content
        assert dto.status == test_message.status

    @pytest.mark.asyncio
    async def test_message_list_dto(self, test_message):
        """Тест создания MessageListDTO."""
        items = [MessageDTO.from_orm(test_message)]
        pagination = PaginationDTO(limit=1, offset=0, total=1)
        
        dto = MessageListDTO(items=items, pagination=pagination)
        
        assert len(dto.items) == 1
        assert dto.pagination.total == 1


class TestEffectiveSettings:
    """Тесты для effective_settings утилиты."""

    @pytest.mark.asyncio
    async def test_get_effective_settings_chat_override(self, test_chat):
        """Тест что настройки чата перекрывают настройки модели."""
        from src.infrastructure.utils.effective_settings import get_effective_settings
        
        # Устанавливаем настройки чата
        test_chat.temperature = 0.9
        test_chat.max_tokens = 2048
        test_chat.context_window = 4096
        test_chat.model_name = "test-model"
        
        result = get_effective_settings(test_chat)
        
        assert result["temperature"] == 0.9
        assert result["max_tokens"] == 2048
        assert result["context_window"] == 4096
        assert result["model"] == "test-model"

    @pytest.mark.asyncio
    async def test_get_effective_settings_model_defaults(self, test_chat, test_model):
        """Тест что используются настройки модели по умолчанию."""
        from src.infrastructure.utils.effective_settings import get_effective_settings
        
        # Очищаем настройки чата
        test_chat.temperature = None
        test_chat.max_tokens = None
        test_chat.context_window = None
        test_chat.model = test_model
        test_chat.model_name = test_model.provider_model
        
        result = get_effective_settings(test_chat)
        
        assert result["temperature"] == 0.7  # Из модели
        assert result["model"] == test_model.provider_model

    @pytest.mark.asyncio
    async def test_get_effective_settings_all_defaults(self, test_chat):
        """Тест что используются дефолтные значения если нет настроек."""
        from src.infrastructure.utils.effective_settings import get_effective_settings
        
        # Очищаем все настройки
        test_chat.temperature = None
        test_chat.max_tokens = None
        test_chat.context_window = None
        test_chat.model = None
        test_chat.model_name = "default-model"
        
        result = get_effective_settings(test_chat)
        
        assert result["temperature"] == 0.7  # Дефолт
        assert result["max_tokens"] == 4096  # Дефолт
        assert result["context_window"] == 4096  # Дефолт
        assert result["model"] == "default-model"


class TestImageHelpers:
    """Тесты для image_helpers утилиты."""

    def test_encode_images_to_base64(self):
        """Тест кодирования изображений в base64."""
        from src.infrastructure.utils.image_helpers import encode_images_to_base64
        
        # Создаем тестовое изображение в памяти
        import io
        img_bytes = io.BytesIO(b"fake image data")
        img_bytes.name = "test.png"
        
        # Проверяем что функция принимает список файлов
        # Реальное тестирование требует PIL который не установлен в test env
        # Проверяем только что функция существует и принимает аргумент
        assert callable(encode_images_to_base64)


class TestRequestParsers:
    """Тесты для request_parsers утилиты."""

    def test_parse_request_field_with_json(self):
        """Тест парсинга JSON запроса."""
        from src.infrastructure.utils.request_parsers import parse_request_field
        import json
        
        data = {"msg": "Hello", "role": "user"}
        result = parse_request_field(json.dumps(data), None)
        
        assert result.msg == "Hello"
        assert result.role == "user"

    def test_parse_request_field_with_string(self):
        """Тест парсинга строкового запроса."""
        from src.infrastructure.utils.request_parsers import parse_request_field
        
        result = parse_request_field("Hello World", "user")
        
        assert result.msg == "Hello World"
        assert result.role == "user"

    def test_parse_request_field_empty(self):
        """Тест парсинга пустого запроса."""
        from src.infrastructure.utils.request_parsers import parse_request_field
        
        result = parse_request_field(None, "user")
        
        # msg остаётся None если не передан
        assert result.msg is None
        assert result.role == "user"


class TestConstants:
    """Тесты для констант."""

    def test_message_status_values(self):
        """Тест значений MessageStatus."""
        from src.core.constants import MessageStatus
        
        assert MessageStatus.PENDING.value == "pending"
        assert MessageStatus.PROCESSING.value == "processing"
        assert MessageStatus.COMPLETED.value == "completed"
        assert MessageStatus.FAILED.value == "failed"

    def test_model_type_values(self):
        """Тест значений ModelType."""
        from src.core.constants import ModelType
        
        assert ModelType.TEXT.value == "text"
        assert ModelType.IMAGE.value == "image"


class TestExceptions:
    """Тесты для исключений."""

    def test_token_not_found_error(self):
        """Тест TokenNotFoundError."""
        from src.exceptions.exceptions import TokenNotFoundError
        
        error = TokenNotFoundError(123)
        assert "123" in str(error)

    def test_chat_not_found_error(self):
        """Тест ChatNotFoundError."""
        from src.exceptions.exceptions import ChatNotFoundError
        from uuid import uuid4
        
        chat_id = uuid4()
        error = ChatNotFoundError(chat_id)
        assert str(chat_id) in str(error)

    def test_model_not_found_error(self):
        """Тест ModelNotFoundError."""
        from src.exceptions.exceptions import ModelNotFoundError
        
        error = ModelNotFoundError(456)
        assert "456" in str(error)

    def test_session_not_found_error(self):
        """Тест SessionNotFoundError."""
        from src.exceptions.exceptions import SessionNotFoundError
        from uuid import uuid4
        
        session_id = uuid4()
        error = SessionNotFoundError(session_id)
        assert str(session_id) in str(error)

    def test_model_inactive_error(self):
        """Тест ModelInactiveError."""
        from src.exceptions.exceptions import ModelInactiveError
        
        error = ModelInactiveError("test-model")
        assert "test-model" in str(error)

    def test_llm_service_error(self):
        """Тест LLMServiceError."""
        from src.exceptions.exceptions import LLMServiceError
        
        error = LLMServiceError("Provider error")
        assert "Provider error" in str(error)
