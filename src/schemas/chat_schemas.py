from typing import List
"""
Схемы для чатов.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.config import settings


class ChatCreateSchema(BaseModel):
    """Схема создания чата."""

    name: str | None = Field(default=None, description="Название чата")
    model_id: int | None = Field(default=None, description="ID модели")
    system_prompt: str | None = Field(
        default=None,
        description="Системный промпт",
        max_length=settings.MAX_PROMPT_LENGTH,
        json_schema_extra={"error_message": f"Системный промпт слишком длинный. Максимум {settings.MAX_PROMPT_LENGTH} символов"},
    )
    temperature: float | None = Field(default=None, description="Температура генерации")
    max_tokens: int | None = Field(default=None, description="Максимум токенов")
    context_window: int | None = Field(default=None, description="Размер контекстного окна")


class ChatUpdateSchema(BaseModel):
    """Схема обновления чата."""

    name: str | None = Field(default=None, description="Название чата")
    system_prompt: str | None = Field(
        default=None,
        description="Системный промпт",
        max_length=settings.MAX_PROMPT_LENGTH,
        json_schema_extra={"error_message": f"Системный промпт слишком длинный. Максимум {settings.MAX_PROMPT_LENGTH} символов"},
    )
    model_id: int | None = Field(default=None, description="ID модели из справочника")
    temperature: float | None = Field(default=None, description="Температура генерации")
    max_tokens: int | None = Field(default=None, description="Максимум токенов")
    context_window: int | None = Field(default=None, description="Размер контекстного окна")


class ChatResponseSchema(BaseModel):
    """Схема ответа чата."""

    id: UUID
    token_id: int
    model_id: int | None = None
    model_name: str | None = None
    name: str | None = None
    system_prompt: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    context_window: int | None = None
    sessions_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ChatListItemSchema(BaseModel):
    """Схема элемента списка чатов."""

    id: UUID
    token_id: int
    model_id: int | None = None
    model_name: str | None = None
    name: str | None = None
    system_prompt: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    context_window: int | None = None
    sessions_count: int = 0

    model_config = {"from_attributes": True}


class ChatListResponseSchema(BaseModel):
    """Схема списка чатов с пагинацией."""

    items: List[ChatListItemSchema]
    total: int
    limit: int | None
    offset: int


class DeleteResponseSchema(BaseModel):
    """Схема ответа при удалении."""

    success: bool
    message: str
