"""
Use Case для удаления чата.
"""

import logging
from uuid import UUID

from src.domain.chat.repositories import ChatRepository
from src.exceptions.domain_exceptions import ChatNotFoundError
from src.schemas.chat_schemas import DeleteResponseSchema
from src.use_cases.base_use_case import BaseUseCase

logger = logging.getLogger(__name__)


class DeleteChatInput:
    """Входные данные для удаления чата."""
    token_id: int
    chat_id: UUID

    def __init__(self, token_id: int, chat_id: UUID):
        self.token_id = token_id
        self.chat_id = chat_id


class DeleteChatUseCase(BaseUseCase[DeleteChatInput, DeleteResponseSchema]):
    """Use Case для удаления чата."""

    def __init__(self, repository: ChatRepository):
        self.repository = repository

    async def _run_logic(self, input_data: DeleteChatInput) -> DeleteResponseSchema:
        """Удаление чата."""
        logger.info(f"Удаление чата ID={input_data.chat_id} для токена ID={input_data.token_id}")
        
        # Проверяем существование чата
        chat = await self.repository.get_by_token_id_and_chat_id(
            input_data.token_id,
            input_data.chat_id
        )

        if not chat:
            raise ChatNotFoundError(chat_id=input_data.chat_id)

        # Удаляем через репозиторий
        await self.repository.delete(input_data.chat_id)
        logger.info(f"Чат ID={input_data.chat_id} удалён")

        return DeleteResponseSchema(
            success=True,
            message="Чат удалён",
        )
