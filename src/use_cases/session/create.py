"""
Use Case для создания сессии.
"""

from uuid import UUID

from src.domain.session.models import Session
from src.domain.session.repositories import SessionRepository
from src.use_cases.base_use_case import BaseUseCase


class CreateSessionInput:
    """Входные данные для создания сессии."""
    token_id: str
    chat_id: UUID

    def __init__(self, token_id: str, chat_id: UUID):
        self.token_id = token_id
        self.chat_id = chat_id


class CreateSessionOutput:
    """Результат создания сессии."""
    session_id: UUID
    token_id: str
    chat_id: UUID

    def __init__(self, session_id: UUID, token_id: str, chat_id: UUID):
        self.session_id = session_id
        self.token_id = token_id
        self.chat_id = chat_id


class CreateSessionUseCase(BaseUseCase[CreateSessionInput, CreateSessionOutput]):
    """Use Case для создания новой сессии."""

    def __init__(self, repository: SessionRepository):
        self.repository = repository

    async def _run_logic(self, input_data: CreateSessionInput) -> CreateSessionOutput:
        """Создание сессии."""
        session = Session(
            token_id=input_data.token_id,
            chat_id=input_data.chat_id,
        )

        created_session = await self.repository.create(session)

        return CreateSessionOutput(
            session_id=created_session.session_id,
            token_id=created_session.token_id,
            chat_id=created_session.chat_id,
        )
