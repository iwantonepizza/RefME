"""
Use Case для получения токена.
"""

import logging
from datetime import datetime

from src.domain.token.models import Token
from src.domain.token.repositories import TokenRepository
from src.exceptions.domain_exceptions import TokenNotFoundError
from src.use_cases.base_use_case import BaseUseCase

logger = logging.getLogger(__name__)


class GetTokenInput:
    """Входные данные для получения токена."""
    token_id: int

    def __init__(self, token_id: int):
        self.token_id = token_id


class GetTokenOutput:
    """Результат получения токена."""
    token_id: int
    token_value: str
    active: bool
    created_at: datetime | None = None
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    chats_count: int = 0
    sessions_count: int = 0

    def __init__(
        self,
        token_id: int,
        token_value: str,
        active: bool,
        created_at: datetime | None = None,
        expires_at: datetime | None = None,
        last_used_at: datetime | None = None,
        chats_count: int = 0,
        sessions_count: int = 0,
    ):
        self.token_id = token_id
        self.token_value = token_value
        self.active = active
        self.created_at = created_at
        self.expires_at = expires_at
        self.last_used_at = last_used_at
        self.chats_count = chats_count
        self.sessions_count = sessions_count

    def model_dump(self) -> dict:
        """Конвертация в dict для сериализации."""
        return {
            "token_id": self.token_id,
            "token_value": self.token_value,
            "active": self.active,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "last_used_at": self.last_used_at,
            "chats_count": self.chats_count,
            "sessions_count": self.sessions_count,
        }


class GetTokenUseCase(BaseUseCase[GetTokenInput, GetTokenOutput]):
    """Use Case для получения токена по ID."""

    def __init__(self, repository: TokenRepository):
        self.repository = repository

    async def _run_logic(self, input_data: GetTokenInput) -> GetTokenOutput:
        """Получение токена."""
        logger.info(f"Получение токена ID={input_data.token_id}")

        token = await self.repository.get_by_id(input_data.token_id)

        if not token:
            raise TokenNotFoundError(token_id=input_data.token_id)

        # Счётчики чатов и сессий удалены из TokenRepository (архитектурное нарушение)
        # При необходимости можно добавить в TokenDTO или вынести в отдельный use case
        chats_count = 0
        sessions_count = 0
        logger.info(f"Токен ID={input_data.token_id} получен")

        return GetTokenOutput(
            token_id=token.token_id,
            token_value=token.token_value,
            active=token.active,
            created_at=token.created_at,
            expires_at=token.expires_at,
            last_used_at=token.last_used_at,
            chats_count=chats_count,
            sessions_count=sessions_count,
        )
