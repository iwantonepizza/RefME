"""
Use Case для получения чата.
"""

import logging
from uuid import UUID

from src.domain.chat.repositories import ChatRepository
from src.exceptions.domain_exceptions import ChatNotFoundError
from src.schemas.chat_schemas import ChatResponseSchema
from src.use_cases.base_use_case import BaseUseCase

logger = logging.getLogger(__name__)


class GetChatInput:
    """Входные данные для получения чата."""
    token_id: int
    chat_id: UUID

    def __init__(self, token_id: int, chat_id: UUID):
        self.token_id = token_id
        self.chat_id = chat_id


class GetChatUseCase(BaseUseCase[GetChatInput, ChatResponseSchema]):
    """Use Case для получения чата по ID."""

    def __init__(self, repository: ChatRepository):
        self.repository = repository

    async def _run_logic(self, input_data: GetChatInput) -> ChatResponseSchema:
        """Получение чата."""
        logger.info(f"Получение чата ID={input_data.chat_id} для токена ID={input_data.token_id}")
        
        chat = await self.repository.get_by_token_id_and_chat_id(
            input_data.token_id,
            input_data.chat_id
        )

        if not chat:
            raise ChatNotFoundError(chat_id=input_data.chat_id)

        # Получаем счётчик сессий
        sessions_count = await self.repository.count_sessions(input_data.chat_id)
        logger.info(f"Чат ID={input_data.chat_id} имеет {sessions_count} сессий")

        return ChatResponseSchema(
            id=chat.chat_id,
            token_id=chat.token_id,
            model_id=chat.model_id,
            model_name=chat.model_name,
            name=chat.name,
            system_prompt=chat.system_prompt,
            temperature=chat.temperature,
            max_tokens=chat.max_tokens,
            context_window=chat.context_window,
            sessions_count=sessions_count,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
        )
