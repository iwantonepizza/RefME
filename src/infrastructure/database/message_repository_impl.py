"""
Реализация репозитория для сообщений.
"""

from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MessageStatus
from src.database.message import ChatMessage
from src.domain.message.filters import MessageFilters
from src.domain.message.models import Message
from src.domain.message.repositories import MessageRepository


class SqlAlchemyMessageRepository(MessageRepository):
    """Реализация репозитория для сообщений на SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: ChatMessage) -> Message:
        """Преобразование ORM модели в Domain модель."""
        return Message(
            message_id=model.id,
            session_id=model.session_id,
            role=model.role,
            content=model.content,
            status=model.status,
            started_at=model.started_at,
            completed_at=model.completed_at,
            created_at=model.created_at,
            deleted_at=model.deleted_at,
        )

    async def get(self, message_id: UUID) -> Message | None:
        """Получение сообщения по ID."""
        return await self.get_by_id(message_id)

    async def list(self, session_id: UUID, limit: int = 100, offset: int = 0,
                   filters: MessageFilters | None = None) -> List[Message]:
        """Получение сообщений по session_id с фильтрами."""
        return await self.get_by_session_id(session_id, limit, offset)

    async def get_by_id(self, message_id: UUID) -> Message | None:
        """Получение сообщения по ID."""
        model = await super().get_by_id(message_id)
        return self._to_domain(model) if model else None

    async def get_by_session_id(
            self, session_id: UUID, limit: int, offset: int
    ) -> List[Message]:
        """Получение сообщений по session_id."""
        query = select(ChatMessage).where(ChatMessage.session_id == session_id)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_last_message_timestamp(self, session_id: UUID) -> datetime | None:
        """Получение времени последнего сообщения в сессии."""
        result = await self.session.execute(
            select(func.max(ChatMessage.created_at)).where(ChatMessage.session_id == session_id)
        )
        return result.scalar()

    async def count_messages(self, session_id: UUID) -> int:
        """Подсчёт количества сообщений в сессии."""
        result = await self.session.execute(
            select(func.count()).select_from(ChatMessage).where(ChatMessage.session_id == session_id)
        )
        return result.scalar() or 0

    async def get_last_n_messages(
            self, session_id: UUID, n: int
    ) -> List[Message]:
        """Получение последних n сообщений."""
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(n)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def create(self, message: Message | dict) -> Message:
        """Создание сообщения."""
        if isinstance(message, dict):
            # Создание из dict
            model = ChatMessage(
                session_id=message.get("session_id"),
                role=message.get("role", "user"),
                content=message.get("content", ""),
                status=message.get("status", MessageStatus.PENDING.value),
            )
        else:
            # Создание из domain модели
            model = ChatMessage(
                session_id=message.session_id,
                role=message.role,
                content=message.content,
                status=message.status,
            )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def delete(self, message_id: UUID) -> None:
        """Удаление сообщения."""
        await super().delete(message_id)
