"""
Use Case для обновления токена.
"""

import logging
from datetime import datetime

from src.domain.token.models import Token
from src.domain.token.repositories import TokenRepository
from src.exceptions.domain_exceptions import TokenNotFoundError
from src.use_cases.base_use_case import BaseUseCase

logger = logging.getLogger(__name__)


class UpdateTokenInput:
    """Входные данные для обновления токена."""
    token_id: int
    active: bool | None = None
    expires_at: datetime | None = None

    def __init__(
        self,
        token_id: int,
        active: bool | None = None,
        expires_at: datetime | None = None,
    ):
        self.token_id = token_id
        self.active = active
        self.expires_at = expires_at


class UpdateTokenOutput:
    """Результат обновления токена."""
    token_id: int
    token_value: str
    active: bool
    created_at: datetime | None = None
    expires_at: datetime | None = None
    last_used_at: datetime | None = None

    def __init__(
        self,
        token_id: int,
        token_value: str,
        active: bool,
        created_at: datetime | None = None,
        expires_at: datetime | None = None,
        last_used_at: datetime | None = None,
    ):
        self.token_id = token_id
        self.token_value = token_value
        self.active = active
        self.created_at = created_at
        self.expires_at = expires_at
        self.last_used_at = last_used_at

    def model_dump(self) -> dict:
        """Конвертация в dict для сериализации."""
        return {
            "token_id": self.token_id,
            "token_value": self.token_value,
            "active": self.active,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "last_used_at": self.last_used_at,
        }


class UpdateTokenUseCase(BaseUseCase[UpdateTokenInput, UpdateTokenOutput]):
    """Use Case для обновления токена."""

    def __init__(self, repository: TokenRepository):
        self.repository = repository

    async def _run_logic(self, input_data: UpdateTokenInput) -> UpdateTokenOutput:
        """Обновление токена."""
        logger.info(f"Обновление токена ID={input_data.token_id}")

        token = await self.repository.get_by_id(input_data.token_id)

        if not token:
            raise TokenNotFoundError(token_id=input_data.token_id)

        # Обновляем поля
        if input_data.active is not None:
            token.active = input_data.active
        if input_data.expires_at is not None:
            token.expires_at = input_data.expires_at

        # Сохраняем через репозиторий
        updated_token = await self.repository.update(token)
        if not updated_token:
            raise TokenNotFoundError(token_id=input_data.token_id)
        logger.info(f"Токен ID={input_data.token_id} обновлён")

        return UpdateTokenOutput(
            token_id=updated_token.token_id,
            token_value=updated_token.token_value,
            active=updated_token.active,
            created_at=updated_token.created_at,
            expires_at=updated_token.expires_at,
            last_used_at=updated_token.last_used_at,
        )
