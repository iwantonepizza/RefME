"""
Реализация репозитория токенов.
"""

from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.api_token import APIToken as APITokenModel
from src.database.chat import ChatSettings
from src.database.session import ChatSession
from src.domain.token.filters import TokenFilters
from src.domain.token.models import Token
from src.domain.token.repositories import TokenRepository


class SqlAlchemyTokenRepository(TokenRepository):
    """
    Реализация репозитория токенов на SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _to_domain(self, model: APITokenModel) -> Token:
        """Преобразование ORM модели в Domain модель."""
        return Token(
            token_id=model.id,
            token_value=model.token,
            active=model.active,
            created_at=model.created_at,
            expires_at=model.expires_at,
            last_used_at=model.last_used_at,
            deleted_at=model.deleted_at,
        )
    
    async def get_by_id(self, id: int) -> Token | None:
        """Получение токена по ID."""
        result = await self.session.execute(
            select(APITokenModel).where(APITokenModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get(self, token_id: int) -> Token | None:
        """Получение токена по ID (алиас для get_by_id)."""
        return await self.get_by_id(token_id)

    async def get_by_token_value(self, token_value: str) -> Token | None:
        """
        Получение токена по значению.
        Проверяет active=True и is_expired.
        """
        result = await self.session.execute(
            select(APITokenModel).where(
                (APITokenModel.token == token_value) &
                (APITokenModel.active == True)
            )
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        token = self._to_domain(model)
        # Проверяем не истёк ли срок действия
        if token.is_expired:
            return None
        return token

    async def get_all(self, limit: int | None = None, offset: int | None = None, order_by: str | None = None) -> List[Token]:
        """Получение всех токенов."""
        query = select(APITokenModel)
        if order_by and hasattr(APITokenModel, order_by):
            query = query.order_by(getattr(APITokenModel, order_by))
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def list(self, limit: int = 100, offset: int = 0,
                   filters: TokenFilters | None = None) -> List[Token]:
        """Получение всех токенов с фильтрами."""
        return await self.get_all(limit=limit, offset=offset)

    async def create(self, token: Token) -> Token:
        """Создание токена."""
        model = APITokenModel(
            token=token.token_value,
            active=token.active,
            expires_at=token.expires_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)
    
    async def update(self, token: Token) -> Token:
        """Обновление токена."""
        result = await self.session.execute(
            select(APITokenModel).where(APITokenModel.id == token.token_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None

        model.active = token.active
        model.expires_at = token.expires_at
        model.last_used_at = token.last_used_at

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def delete(self, token_id: int) -> None:
        """Удаление токена."""
        result = await self.session.execute(
            select(APITokenModel).where(APITokenModel.id == token_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)

    async def count(self, filters: TokenFilters | None = None) -> int:
        """Подсчёт количества токенов."""
        query = select(func.count()).select_from(APITokenModel)
        if filters:
            # Простая реализация фильтрации
            if filters.active is not None:
                query = query.where(APITokenModel.active == filters.active)
            if filters.is_deleted is not None:
                query = query.where(APITokenModel.deleted_at != None if not filters.is_deleted else APITokenModel.deleted_at == None)
        result = await self.session.execute(query)
        return result.scalar() or 0
