"""
Use Case для получения списка токенов.
"""

import logging

from src.domain.token.models import Token
from src.domain.token.repositories import TokenRepository
from src.use_cases.base_use_case import BaseUseCase
from src.use_cases.dto import TokenDTO, TokenListDTO, PaginationDTO

logger = logging.getLogger(__name__)


class ListTokensInput:
    """Входные данные для получения списка токенов."""
    limit: int | None = 100
    offset: int | None = 0

    def __init__(self, limit: int | None = 100, offset: int | None = 0):
        self.limit = limit
        self.offset = offset


class ListTokensUseCase(BaseUseCase[ListTokensInput, TokenListDTO]):
    """Use Case для получения списка токенов."""

    def __init__(self, repository: TokenRepository):
        self.repository = repository

    async def _run_logic(self, input_data: ListTokensInput) -> TokenListDTO:
        """Получение списка токенов."""
        logger.info(f"Получение списка токенов, limit={input_data.limit}, offset={input_data.offset}")

        # Получаем список токенов
        tokens = await self.repository.list(
            limit=input_data.limit,
            offset=input_data.offset
        )

        # Получаем общее количество
        total = await self.repository.count()

        # Конвертируем в DTO
        # Счётчики чатов и сессий удалены из TokenRepository (архитектурное нарушение)
        items = [TokenDTO.from_orm(token, chats_count=0, sessions_count=0) for token in tokens]

        return TokenListDTO(
            items=items,
            pagination=PaginationDTO(
                limit=input_data.limit,
                offset=input_data.offset,
                total=total,
            ),
        )
