"""
Use Case для получения списка чатов.
"""

import logging

from src.domain.chat.repositories import ChatRepository
from src.schemas.chat_schemas import ChatListResponseSchema, ChatListItemSchema
from src.use_cases.base_use_case import BaseUseCase

logger = logging.getLogger(__name__)


class ListChatsInput:
    """Входные данные для получения списка чатов."""
    token_id: int
    limit: int | None = None
    offset: int | None = 0

    def __init__(self, token_id: int, limit: int | None = None, offset: int | None = 0):
        self.token_id = token_id
        self.limit = limit or 100
        self.offset = offset or 0


class ListChatsUseCase(BaseUseCase[ListChatsInput, ChatListResponseSchema]):
    """Use Case для получения списка чатов токена."""

    def __init__(self, repository: ChatRepository):
        self.repository = repository

    async def _run_logic(self, input_data: ListChatsInput) -> ChatListResponseSchema:
        """Получение списка чатов."""
        logger.info(f"Получение списка чатов для токена ID={input_data.token_id}")
        
        # Получаем список чатов
        chats = await self.repository.list(
            token_id=input_data.token_id,
            limit=input_data.limit,
            offset=input_data.offset
        )

        # Получаем общее количество
        total = await self.repository.count(filters={"token_id": input_data.token_id})

        # Получаем счётчик сессий для каждого чата
        items = []
        for chat in chats:
            sessions_count = await self.repository.count_sessions(chat.chat_id)
            items.append(ChatListItemSchema(
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
            ))

        logger.info(f"Получено {len(items)} чатов для токена ID={input_data.token_id}")
        
        return ChatListResponseSchema(
            items=items,
            total=total,
            limit=input_data.limit,
            offset=input_data.offset,
        )
