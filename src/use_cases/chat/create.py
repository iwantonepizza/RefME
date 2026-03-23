"""
Use Case для создания чата.
"""

import logging
from typing import TYPE_CHECKING
from uuid import UUID

from src.domain.chat.models import Chat
from src.domain.chat.repositories import ChatRepository
from src.schemas.chat_schemas import ChatCreateSchema, ChatResponseSchema
from src.use_cases.base_use_case import BaseUseCase

logger = logging.getLogger(__name__)


class CreateChatInput(ChatCreateSchema):
    """Входные данные для создания чата."""
    token_id: int


class CreateChatUseCase(BaseUseCase[CreateChatInput, ChatResponseSchema]):
    """Use Case для создания нового чата."""

    def __init__(self, repository: ChatRepository):
        self.repository = repository

    async def _run_logic(self, input_data: CreateChatInput) -> ChatResponseSchema:
        """Создание чата."""
        logger.info(f"Создание чата для токена ID={input_data.token_id}")

        # Создаём domain модель (валидация происходит в __init__)
        chat = Chat(
            token_id=input_data.token_id,
            model_id=input_data.model_id,
            name=input_data.name,
            system_prompt=input_data.system_prompt,
            temperature=input_data.temperature,
            max_tokens=input_data.max_tokens,
            context_window=input_data.context_window,
        )

        # Сохраняем через репозиторий
        created_chat = await self.repository.create(chat)
        logger.info(f"Чат создан с ID={created_chat.chat_id}")

        # Получаем счётчик сессий
        sessions_count = await self.repository.count_sessions(created_chat.chat_id)

        return ChatResponseSchema(
            id=created_chat.chat_id,
            token_id=created_chat.token_id,
            model_id=created_chat.model_id,
            model_name=created_chat.model_name,
            name=created_chat.name,
            system_prompt=created_chat.system_prompt,
            temperature=created_chat.temperature,
            max_tokens=created_chat.max_tokens,
            context_window=created_chat.context_window,
            sessions_count=sessions_count,
            created_at=created_chat.created_at,
        )
