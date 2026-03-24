from typing import List
"""
Use Case для получения списка сессий.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.session.repositories import SessionRepository
from src.use_cases.base_use_case import BaseUseCase


@dataclass
class SessionItemOutput:
    """Элемент списка сессий."""
    id: UUID
    token_id: str
    chat_id: UUID
    created_at: datetime | None = None
    deleted_at: datetime | None = None
    last_activity_at: datetime | None = None
    messages_count: int = 0


@dataclass
class ListSessionsInput:
    """Входные данные для получения списка сессий."""
    token_id: str
    limit: int | None = None
    offset: int | None = 0


@dataclass
class ListSessionsOutput:
    """Результат получения списка сессий."""
    items: List[SessionItemOutput]
    total: int
    limit: int | None
    offset: int


class ListSessionsUseCase(BaseUseCase[ListSessionsInput, ListSessionsOutput]):
    """Use Case для получения списка сессий токена."""

    def __init__(self, repository: SessionRepository, message_repository=None):
        self.repository = repository
        self.message_repository = message_repository

    async def _run_logic(self, input_data: ListSessionsInput) -> ListSessionsOutput:
        """Получение списка сессий."""
        # Получаем список сессий
        sessions = await self.repository.list_by_token_id(
            token_id=input_data.token_id,
            limit=input_data.limit or 100,
            offset=input_data.offset or 0
        )

        # Получаем общее количество
        from src.domain.session.filters import SessionFilters
        total = await self.repository.count(filters=SessionFilters(token_id=input_data.token_id))

        # Получаем дополнительную информацию для каждой сессии
        items = []
        for session in sessions:
            last_activity_at = None
            messages_count = 0
            if self.message_repository:
                last_activity_at = await self.message_repository.get_last_message_timestamp(session.session_id)
                messages_count = await self.message_repository.count_messages(session.session_id)

            items.append(SessionItemOutput(
                id=session.session_id,
                token_id=session.token_id,
                chat_id=session.chat_id,
                created_at=session.created_at,
                deleted_at=session.deleted_at,
                last_activity_at=last_activity_at,
                messages_count=messages_count,
            ))

        return ListSessionsOutput(
            items=items,
            total=total,
            limit=input_data.limit,
            offset=input_data.offset or 0,
        )
