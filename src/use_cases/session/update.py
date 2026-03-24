"""
Use Case для обновления сессии.
"""

import logging
from uuid import UUID

from src.domain.session.models import Session
from src.domain.session.repositories import SessionRepository
from src.exceptions.domain_exceptions import SessionNotFoundError
from src.use_cases.base_use_case import BaseUseCase

logger = logging.getLogger(__name__)


class UpdateSessionInput:
    """Входные данные для обновления сессии."""
    session_id: UUID
    chat_id: UUID

    def __init__(self, session_id: UUID, chat_id: UUID):
        self.session_id = session_id
        self.chat_id = chat_id


class UpdateSessionOutput:
    """Результат обновления сессии."""
    session_id: UUID
    token_id: str
    chat_id: UUID
    success: bool

    def __init__(self, session_id: UUID, token_id: str, chat_id: UUID, success: bool = True):
        self.session_id = session_id
        self.token_id = token_id
        self.chat_id = chat_id
        self.success = success


class UpdateSessionUseCase(BaseUseCase[UpdateSessionInput, UpdateSessionOutput]):
    """Use Case для обновления сессии (перепривязка к чату)."""

    def __init__(self, repository: SessionRepository):
        self.repository = repository

    async def _run_logic(self, input_data: UpdateSessionInput) -> UpdateSessionOutput:
        """Обновление сессии."""
        logger.info(f"Обновление сессии ID={input_data.session_id}, привязка к чату ID={input_data.chat_id}")

        # Получаем сессию
        session = await self.repository.get(input_data.session_id)

        if not session:
            raise SessionNotFoundError(session_id=input_data.session_id)

        # Обновляем chat_id
        session.chat_id = input_data.chat_id

        # Сохраняем через репозиторий
        updated_session = await self.repository.update(session)
        if not updated_session:
            raise SessionNotFoundError(session_id=input_data.session_id)

        logger.info(f"Сессия ID={input_data.session_id} обновлена, привязана к чату ID={input_data.chat_id}")

        return UpdateSessionOutput(
            session_id=updated_session.session_id,
            token_id=updated_session.token_id,
            chat_id=updated_session.chat_id,
            success=True,
        )
