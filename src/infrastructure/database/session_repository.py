"""
Реализация репозитория для сессий.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import ChatSession
from src.domain.session.models import Session as SessionDomain
from src.domain.session.repositories import SessionRepository as SessionRepositoryInterface


class SqlAlchemySessionRepository(SessionRepositoryInterface):
    """Репозиторий для сессий."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: ChatSession) -> SessionDomain:
        """Преобразование ORM модели в Domain модель."""
        return SessionDomain(
            session_id=model.id,
            token_id=model.token_id,
            chat_id=model.chat_id,
            created_at=model.created_at,
            deleted_at=model.deleted_at,
        )

    async def get_by_token_id_and_session_id(
        self, token_id: str, session_id: UUID
    ) -> SessionDomain | None:
        """Получение сессии по token_id и session_id."""
        result = await self.session.execute(
            select(ChatSession).where(
                (ChatSession.token_id == token_id) &
                (ChatSession.id == session_id)
            )
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_token_id(
        self, token_id: str, limit: int, offset: int
    ) -> List[SessionDomain]:
        """Получение сессий по token_id."""
        query = select(ChatSession).where(ChatSession.token_id == token_id)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def list(self, token_id: str, limit: int = 100, offset: int = 0,
                   filters: dict = None) -> List[SessionDomain]:
        """Получение сессий по token_id с фильтрами (алиас для get_by_token_id)."""
        return await self.get_by_token_id(token_id, limit, offset)

    async def get_by_chat_id(self, chat_id: UUID) -> List[SessionDomain]:
        """Получение сессий по chat_id."""
        result = await self.session.execute(
            select(ChatSession).where(ChatSession.chat_id == chat_id)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_by_id(self, session_id: UUID) -> SessionDomain | None:
        """Получение сессии по ID."""
        result = await self.session.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get(self, session_id: UUID) -> SessionDomain | None:
        """Получение сессии по ID (алиас для get_by_id)."""
        return await self.get_by_id(session_id)

    async def create(self, session: SessionDomain) -> SessionDomain:
        """Создание сессии."""
        model = ChatSession(
            token_id=session.token_id,
            chat_id=session.chat_id,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(self, session: SessionDomain) -> SessionDomain:
        """Обновление сессии."""
        result = await self.session.execute(
            select(ChatSession).where(ChatSession.id == session.session_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None

        model.chat_id = session.chat_id

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def delete(self, session_id: UUID) -> None:
        """Удаление сессии."""
        result = await self.session.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)

    async def count(self, filters: dict = None) -> int:
        """Подсчёт количества сессий."""
        query = select(func.count()).select_from(ChatSession)
        if filters:
            for field, value in filters.items():
                if value is not None:
                    query = query.where(getattr(ChatSession, field) == value)
        result = await self.session.execute(query)
        return result.scalar() or 0
