"""
Use Case для обновления чата.
"""

import logging
from uuid import UUID

from src.domain.chat.repositories import ChatRepository
from src.exceptions.domain_exceptions import ChatNotFoundError
from src.schemas.chat_schemas import ChatResponseSchema, ChatUpdateSchema
from src.use_cases.base_use_case import BaseUseCase

logger = logging.getLogger(__name__)


class UpdateChatInput(ChatUpdateSchema):
    """Входные данные для обновления чата."""
    token_id: int
    chat_id: UUID


class UpdateChatUseCase(BaseUseCase[UpdateChatInput, ChatResponseSchema]):
    """Use Case для обновления чата."""

    def __init__(self, repository: ChatRepository):
        self.repository = repository

    async def _run_logic(self, input_data: UpdateChatInput) -> ChatResponseSchema:
        """Обновление чата."""
        logger.info(f"Обновление чата ID={input_data.chat_id} для токена ID={input_data.token_id}")

        # Проверяем существование чата
        chat = await self.repository.get_by_token_id_and_chat_id(
            input_data.token_id,
            input_data.chat_id
        )

        if not chat:
            raise ChatNotFoundError(chat_id=input_data.chat_id)

        # Обновляем поля
        if input_data.name is not None:
            chat.name = input_data.name
        if input_data.system_prompt is not None:
            chat.system_prompt = input_data.system_prompt
        if input_data.model_id is not None:
            chat.model_id = input_data.model_id
        if input_data.temperature is not None:
            chat.temperature = input_data.temperature
        if input_data.max_tokens is not None:
            chat.max_tokens = input_data.max_tokens
        if input_data.context_window is not None:
            chat.context_window = input_data.context_window

        # Сохраняем через репозиторий
        updated_chat = await self.repository.update(chat)
        logger.info(f"Чат ID={input_data.chat_id} обновлён")

        # Получаем счётчик сессий
        sessions_count = await self.repository.count_sessions(input_data.chat_id)

        return ChatResponseSchema(
            id=updated_chat.chat_id,
            token_id=updated_chat.token_id,
            model_id=updated_chat.model_id,
            model_name=updated_chat.model_name,
            name=updated_chat.name,
            system_prompt=updated_chat.system_prompt,
            temperature=updated_chat.temperature,
            max_tokens=updated_chat.max_tokens,
            context_window=updated_chat.context_window,
            sessions_count=sessions_count,
            created_at=updated_chat.created_at,
            updated_at=updated_chat.updated_at,
        )
