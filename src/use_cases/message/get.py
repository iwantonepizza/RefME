from typing import Optional
"""
Use Case для получения сообщений сессии.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.domain.message.repositories import MessageRepository
from src.use_cases.base_use_case import BaseUseCase


class MessageItemOutput:
    """Элемент сообщения."""
    id: UUID  # alias для message_id
    session_id: UUID
    role: str
    content: str
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    deleted_at: datetime | None = None

    def __init__(
        self,
        message_id: UUID,
        session_id: UUID,
        role: str,
        content: str,
        status: str,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        created_at: datetime | None = None,
        deleted_at: datetime | None = None,
    ):
        self.id = message_id  # Конвертируем message_id → id
        self.session_id = session_id
        self.role = role
        self.content = content
        self.status = status
        self.started_at = started_at
        self.completed_at = completed_at
        self.created_at = created_at
        self.deleted_at = deleted_at


class GetMessagesInput:
    """Входные данные для получения сообщений."""
    session_id: UUID
    limit: int | None = None
    offset: int | None = 0

    def __init__(self, session_id: UUID, limit: int | None = None, offset: int | None = 0):
        self.session_id = session_id
        self.limit = limit or 100
        self.offset = offset or 0


class GetMessagesOutput:
    """Результат получения сообщений."""
    items: List[MessageItemOutput]
    total: int
    limit: int | None
    offset: int

    def __init__(
        self,
        items: List[MessageItemOutput],
        total: int,
        limit: int | None,
        offset: int,
    ):
        self.items = items
        self.total = total
        self.limit = limit
        self.offset = offset


class GetMessagesUseCase(BaseUseCase[GetMessagesInput, GetMessagesOutput]):
    """Use Case для получения сообщений сессии."""

    def __init__(self, repository: MessageRepository):
        self.repository = repository

    async def _run_logic(self, input_data: GetMessagesInput) -> GetMessagesOutput:
        """Получение сообщений."""
        # Получаем список сообщений
        messages = await self.repository.list(
            session_id=input_data.session_id,
            limit=input_data.limit,
            offset=input_data.offset
        )

        # Получаем общее количество
        total = await self.repository.count(filters={"session_id": input_data.session_id})

        # Преобразуем в output модели
        items = [MessageItemOutput(
            message_id=msg.message_id,
            session_id=msg.session_id,
            role=msg.role,
            content=msg.content,
            status=msg.status,
            started_at=msg.started_at,
            completed_at=msg.completed_at,
            created_at=msg.created_at,
            deleted_at=msg.deleted_at,
        ) for msg in messages]

        return GetMessagesOutput(
            items=items,
            total=total,
            limit=input_data.limit,
            offset=input_data.offset,
        )
