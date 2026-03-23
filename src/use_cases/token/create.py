"""Use Case для создания токена."""

import logging
import secrets
from datetime import datetime, timezone

from src.domain.token.models import Token
from src.domain.chat.models import Chat
from src.domain.chat.repositories import ChatRepository
from src.domain.token.repositories import TokenRepository
from src.use_cases.base_use_case import BaseUseCase

logger = logging.getLogger(__name__)


class CreateTokenInput:
    """Входные данные для создания токена."""
    expires_at: datetime | None = None

    def __init__(self, expires_at: datetime | None = None):
        self.expires_at = expires_at


class CreateTokenOutput:
    """Результат создания токена."""

    def __init__(
        self,
        token_id: int,
        token_value: str,
        active: bool,
        created_at: datetime | None = None,
        expires_at: datetime | None = None,
    ):
        self.token_id = token_id
        self.token_value = token_value
        self.active = active
        self.created_at = created_at
        self.expires_at = expires_at

    def model_dump(self) -> dict:
        """Конвертация в dict."""
        return {
            "token_id": self.token_id,
            "token_value": self.token_value,
            "active": self.active,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
        }

    @classmethod
    def from_domain_token(cls, token: Token) -> "CreateTokenOutput":
        """Создание из domain модели."""
        return cls(
            token_id=token.token_id,
            token_value=token.token_value,
            active=token.active,
            created_at=token.created_at,
            expires_at=token.expires_at,
        )


class CreateTokenUseCase(BaseUseCase[CreateTokenInput, CreateTokenOutput]):
    """Use Case для создания нового токена."""

    def __init__(
        self,
        token_repository: TokenRepository,
        chat_repository: ChatRepository,
    ):
        self.token_repository = token_repository
        self.chat_repository = chat_repository

    async def _run_logic(self, input_data: CreateTokenInput) -> CreateTokenOutput:
        """Создание токена."""
        logger.info("Создание нового токена")

        token_value = secrets.token_hex(32)

        token = Token(
            token_value=token_value,
            active=True,
            expires_at=input_data.expires_at,
        )

        created_token = await self.token_repository.create(token)
        logger.info(f"Токен создан с ID={created_token.token_id}")

        default_chat = Chat(
            token_id=created_token.token_id,
            name="Default Chat",
        )
        await self.chat_repository.create(default_chat)
        logger.info(f"Чат по умолчанию создан для токена ID={created_token.token_id}")

        return CreateTokenOutput.from_domain_token(created_token)
