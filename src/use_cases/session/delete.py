"""
Use Case для удаления сессии.
"""

from dataclasses import dataclass
from uuid import UUID

from src.domain.session.repositories import SessionRepository
from src.exceptions.domain_exceptions import SessionNotFoundError
from src.use_cases.base_use_case import BaseUseCase


@dataclass
class DeleteSessionInput:
    """Входные данные для удаления сессии."""
    token_id: str
    session_id: UUID


@dataclass
class DeleteSessionOutput:
    """Результат удаления сессии."""
    success: bool
    message: str


class DeleteSessionUseCase(BaseUseCase[DeleteSessionInput, DeleteSessionOutput]):
    """Use Case для удаления сессии."""

    def __init__(self, repository: SessionRepository):
        self.repository = repository

    async def _run_logic(self, input_data: DeleteSessionInput) -> DeleteSessionOutput:
        """Удаление сессии."""
        # Проверяем существование сессии
        session = await self.repository.get_by_token_id_and_session_id(
            input_data.token_id,
            input_data.session_id
        )

        if not session:
            raise SessionNotFoundError(session_id=input_data.session_id)

        # Удаляем через репозиторий
        await self.repository.delete(input_data.session_id)

        return DeleteSessionOutput(
            success=True,
            message="Сессия удалена",
        )
