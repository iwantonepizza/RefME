"""
Use Case для удаления токена.
"""

import logging

from src.domain.token.repositories import TokenRepository
from src.exceptions.domain_exceptions import TokenNotFoundError
from src.use_cases.base_use_case import BaseUseCase

logger = logging.getLogger(__name__)


class DeleteTokenInput:
    """Входные данные для удаления токена."""
    token_id: int

    def __init__(self, token_id: int):
        self.token_id = token_id


class DeleteTokenOutput:
    """Результат удаления токена."""
    success: bool
    message: str

    def __init__(self, success: bool, message: str):
        self.success = success
        self.message = message


class DeleteTokenUseCase(BaseUseCase[DeleteTokenInput, DeleteTokenOutput]):
    """Use Case для удаления токена по ID."""

    def __init__(self, repository: TokenRepository):
        self.repository = repository

    async def _run_logic(self, input_data: DeleteTokenInput) -> DeleteTokenOutput:
        """Удаление токена."""
        logger.info(f"Удаление токена ID={input_data.token_id}")

        # Проверяем существование токена
        token = await self.repository.get(input_data.token_id)

        if not token:
            raise TokenNotFoundError(token_id=input_data.token_id)

        # Удаляем через репозиторий
        await self.repository.delete(input_data.token_id)
        logger.info(f"Токен ID={input_data.token_id} удалён")

        return DeleteTokenOutput(
            success=True,
            message="Токен удалён",
        )
