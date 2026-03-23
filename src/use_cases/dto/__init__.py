"""
DTO (Data Transfer Objects) для передачи данных между слоями.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.core.constants import ModelType

if TYPE_CHECKING:
    from src.database.api_token import APIToken
    from src.database.chat import ChatSettings
    from src.database.llm_model import LLMModel
    from src.database.message import ChatMessage
    from src.database.session import ChatSession

# ==================== Pagination DTO ====================


class PaginationDTO(BaseModel):
    """Базовая пагинация."""

    limit: int
    offset: int
    total: int


class ListLimitOffsetOutputDTO(BaseModel):
    """Базовый DTO для списочных ответов с пагинацией."""

    items: list
    pagination: PaginationDTO


# ==================== Model DTO ====================


class ModelDTO(BaseModel):
    """DTO для LLM модели."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    provider_model: str
    provider: str  # Провайдер: ollama или vllm
    type: str
    active: bool
    max_tokens: int | None = None
    context_window: int | None = None
    temperature: float | None = None
    description: str | None = None
    chats_count: int = 0

    @classmethod
    def from_orm(cls, model: "LLMModel", chats_count: int | None = None) -> "ModelDTO":
        """Создание DTO из SQLAlchemy или domain модели."""
        # Проверяем тип модели (domain или ORM)
        model_id = getattr(model, 'id', None) or getattr(model, 'model_id', 0)
        model_type = getattr(model, 'type', None)
        model_types = getattr(model, 'types', [])
        
        # Если type не найден, берём первый элемент из types list
        type_value = model_type.value if hasattr(model_type, 'value') else (model_types[0] if model_types else "text")
        
        return cls(
            id=model_id,
            name=model.name,
            provider_model=model.provider_model,
            provider=model.provider,
            type=type_value,
            active=model.active,
            max_tokens=model.max_tokens,
            context_window=model.context_window,
            temperature=model.temperature,
            description=model.description,
            chats_count=chats_count or 0,
        )


class ModelListDTO(BaseModel):
    """Список моделей с пагинацией."""

    items: List[ModelDTO]
    pagination: PaginationDTO


# ==================== Chat DTO ====================


class ChatDTO(BaseModel):
    """DTO для чата."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    token_id: int
    model_id: int | None = None
    # model_name убран - дублируется в связанной модели
    name: str | None = None
    system_prompt: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    context_window: int | None = None
    sessions_count: int = 0  # Счётчик сессий

    @classmethod
    def from_orm(cls, chat: "ChatSettings", sessions_count: int | None = None) -> "ChatDTO":
        """Создание DTO из SQLAlchemy модели."""
        return cls(
            id=chat.id,
            token_id=chat.token_id,
            model_id=chat.model_id,
            name=chat.name,
            system_prompt=chat.system_prompt,
            temperature=chat.temperature,
            max_tokens=chat.max_tokens,
            context_window=chat.context_window,
            sessions_count=sessions_count or 0,
        )


class ChatListDTO(BaseModel):
    """Список чатов с пагинацией."""

    items: List[ChatDTO]
    pagination: PaginationDTO


# ==================== Session DTO ====================


class SessionDTO(BaseModel):
    """DTO для сессии."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    token_id: str
    chat_id: UUID
    created_at: datetime
    last_activity_at: datetime | None = None  # Последняя активность
    messages_count: int = 0  # Счётчик сообщений

    @classmethod
    def from_orm(cls, session: "ChatSession", last_activity_at: datetime | None = None, messages_count: int | None = None) -> "SessionDTO":
        """Создание DTO из SQLAlchemy модели."""
        return cls(
            id=session.id,
            token_id=session.token_id,
            chat_id=session.chat_id,
            created_at=session.created_at,
            last_activity_at=last_activity_at,
            messages_count=messages_count or 0,
        )


class SessionListDTO(BaseModel):
    """Список сессий с пагинацией."""

    items: List[SessionDTO]
    pagination: PaginationDTO


# ==================== Message DTO ====================


class MessageDTO(BaseModel):
    """DTO для сообщения."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    role: str
    content: str
    status: str
    process_at: datetime | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @classmethod
    def from_orm(cls, message: "ChatMessage") -> "MessageDTO":
        """Создание DTO из SQLAlchemy или domain модели."""
        # Проверяем тип модели и получаем ID
        message_id = getattr(message, 'id', None) or getattr(message, 'message_id', None)
        session_id = getattr(message, 'session_id', None)
        
        return cls(
            id=message_id,
            session_id=session_id,
            role=message.role,
            content=message.content,
            status=message.status,
            process_at=getattr(message, 'started_at', None) or getattr(message, 'process_at', None),
            created_at=message.created_at,
        )


class MessageListDTO(BaseModel):
    """Список сообщений с пагинацией."""

    items: List[MessageDTO]
    pagination: PaginationDTO


# ==================== Token DTO ====================


class TokenDTO(BaseModel):
    """DTO для API токена."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    token_value: str
    active: bool
    created_at: datetime | None = None
    last_used_at: datetime | None = None
    chats_count: int = 0  # Счётчик чатов
    sessions_count: int = 0  # Счётчик сессий

    @classmethod
    def from_orm(cls, token, chats_count: int | None = None, sessions_count: int | None = None) -> "TokenDTO":
        """Создание DTO из SQLAlchemy или domain модели."""
        # Проверяем тип модели и получаем значение токена
        token_value = getattr(token, 'token_value', None) or getattr(token, 'token', None)
        
        # Получаем ID - проверяем оба варианта (id для ORM, token_id для domain)
        token_id = getattr(token, 'id', None) or getattr(token, 'token_id', 0)

        return cls(
            id=token_id,
            token_value=token_value,
            active=token.active,
            created_at=token.created_at,
            last_used_at=token.last_used_at,
            chats_count=chats_count or 0,
            sessions_count=sessions_count or 0,
        )


class TokenListDTO(BaseModel):
    """Список токенов с пагинацией."""

    items: List[TokenDTO]
    pagination: PaginationDTO


# ==================== LLM DTO ====================


class LLMRequestDTO(BaseModel):
    """DTO для LLM запроса."""

    model: str
    messages: List[dict]
    temperature: float = 0.7
    max_tokens: int = 4096
    context_window: int = 4096


class LLMResponseDTO(BaseModel):
    """DTO для LLM ответа."""

    response: str
    latency: float
    model: str | None = None


class LLMStreamResponseDTO(BaseModel):
    """DTO для LLM стрим ответа."""

    chunk: str
    latency: float | None = None
