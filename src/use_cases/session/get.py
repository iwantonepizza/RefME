from typing import List, Optional
"""
Use Case для получения сессии.
"""

from datetime import datetime
from uuid import UUID

from src.domain.session.repositories import SessionRepository
from src.exceptions.domain_exceptions import InvalidInputError, SessionNotFoundError
from src.use_cases.base_use_case import BaseUseCase


class GetSessionInput:
    """Входные данные для получения сессии."""
    token_id: str | None = None
    session_id: UUID | None = None

    def __init__(self, token_id: str, session_id: UUID):
        self.token_id = token_id
        self.session_id = session_id


class GetSessionOutput:
    """Результат получения сессии."""
    session_id: UUID
    token_id: str
    chat_id: UUID
    created_at: datetime | None = None
    deleted_at: datetime | None = None
    last_activity_at: datetime | None = None
    messages_count: int = 0

    def __init__(
        self,
        session_id: UUID,
        token_id: str,
        chat_id: UUID,
        created_at: datetime | None = None,
        deleted_at: datetime | None = None,
        last_activity_at: datetime | None = None,
        messages_count: int = 0,
    ):
        self.session_id = session_id
        self.token_id = token_id
        self.chat_id = chat_id
        self.created_at = created_at
        self.deleted_at = deleted_at
        self.last_activity_at = last_activity_at
        self.messages_count = messages_count


class GetSessionUseCase(BaseUseCase[GetSessionInput, GetSessionOutput]):
    """Use Case для получения сессии по ID."""

    def __init__(self, repository: SessionRepository, message_repository=None):
        self.repository = repository
        self.message_repository = message_repository

    async def _run_logic(self, input_data: GetSessionInput) -> GetSessionOutput:
        """Получение сессии."""
        # Получаем сессию
        if input_data.token_id and input_data.session_id:
            session = await self.repository.get_by_token_id_and_session_id(
                input_data.token_id,
                input_data.session_id
            )
        elif input_data.session_id:
            session = await self.repository.get_by_id(input_data.session_id)
        else:
            raise InvalidInputError("session_id is required")

        if not session:
            raise SessionNotFoundError(session_id=input_data.session_id)

        # Получаем дополнительную информацию если предоставлен message_repository
        last_activity_at = None
        messages_count = 0
        if self.message_repository:
            last_activity_at = await self.message_repository.get_last_message_timestamp(session.session_id)
            messages_count = await self.message_repository.count_messages(session.session_id)

        return GetSessionOutput(
            session_id=session.session_id,
            token_id=session.token_id,
            chat_id=session.chat_id,
            created_at=session.created_at,
            deleted_at=session.deleted_at,
            last_activity_at=last_activity_at,
            messages_count=messages_count,
        )
