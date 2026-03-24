"""
Реализация репозитория чатов.
"""

from typing import List
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database.chat import ChatSettings as ChatSettingsModel
from src.database.llm_model import LLMModel
from src.database.session import ChatSession
from src.domain.chat.filters import ChatFilters
from src.domain.chat.models import Chat
from src.domain.chat.repositories import ChatRepository


class SqlAlchemyChatRepository(ChatRepository):
    """Реализация репозитория чатов на SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _to_domain(self, model: ChatSettingsModel) -> Chat:
        """Преобразование ORM модели в Domain модель."""
        # Если model_name не указан, но есть связанная модель, берём provider_model из неё
        model_name = model.model_name
        if not model_name and hasattr(model, 'model') and model.model:
            model_name = model.model.provider_model

        return Chat(
            token_id=model.token_id,
            chat_id=model.id,
            model_id=model.model_id,
            model_name=model_name,
            name=model.name,
            system_prompt=model.system_prompt,
            temperature=model.temperature,
            max_tokens=model.max_tokens,
            context_window=model.context_window,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
    
    async def get_by_id(self, chat_id: UUID) -> Chat | None:
        """Получение чата по ID."""
        result = await self.session.execute(
            select(ChatSettingsModel).where(ChatSettingsModel.id == chat_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get(self, chat_id: UUID) -> Chat | None:
        """Получение чата по ID (алиас для get_by_id)."""
        return await self.get_by_id(chat_id)

    async def get_by_token_id_and_chat_id(self, token_id: int, chat_id: UUID) -> Chat | None:
        """Получение чата по token_id и chat_id с загруженной моделью."""
        result = await self.session.execute(
            select(ChatSettingsModel)
            .options(joinedload(ChatSettingsModel.model))
            .where(
                (ChatSettingsModel.token_id == token_id) &
                (ChatSettingsModel.id == chat_id)
            )
        )
        model = result.unique().scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_by_token_id(self, token_id: int, limit: int = 100, offset: int = 0,
                   filters: ChatFilters | None = None) -> List[Chat]:
        """Получение чатов токена с загруженными моделями."""
        result = await self.session.execute(
            select(ChatSettingsModel)
            .options(joinedload(ChatSettingsModel.model))
            .where(ChatSettingsModel.token_id == token_id)
            .order_by(ChatSettingsModel.name)
            .limit(limit)
            .offset(offset)
        )
        models = result.unique().scalars().all()
        return [self._to_domain(m) for m in models]

    async def list(self, token_id: int, limit: int = 100, offset: int = 0,
                   filters: ChatFilters | None = None) -> List[Chat]:
        """Получение списка чатов с фильтрами (алиас для list_by_token_id)."""
        return await self.list_by_token_id(token_id, limit, offset, filters)

    async def create(self, chat: Chat) -> Chat:
        """Создание чата."""
        model = ChatSettingsModel(
            token_id=chat.token_id,
            model_id=chat.model_id,
            model_name=chat.model_name,
            name=chat.name,
            system_prompt=chat.system_prompt,
            temperature=chat.temperature,
            max_tokens=chat.max_tokens,
            context_window=chat.context_window,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)

        # Если указан model_id, загружаем модель чтобы получить provider_model
        if model.model_id:
            result = await self.session.execute(
                select(LLMModel).where(LLMModel.id == model.model_id)
            )
            llm_model = result.scalar_one_or_none()
            if llm_model:
                model.model_name = llm_model.provider_model

        return self._to_domain(model)

    async def update(self, chat: Chat) -> Chat:
        """Обновление чата."""
        result = await self.session.execute(
            select(ChatSettingsModel).where(ChatSettingsModel.id == chat.chat_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None

        model.name = chat.name
        model.system_prompt = chat.system_prompt
        model.model_id = chat.model_id
        model.model_name = chat.model_name
        model.temperature = chat.temperature
        model.max_tokens = chat.max_tokens
        model.context_window = chat.context_window

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def delete(self, chat_id: UUID) -> None:
        """Удаление чата."""
        result = await self.session.execute(
            select(ChatSettingsModel).where(ChatSettingsModel.id == chat_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)

    async def count(self, filters: ChatFilters | None = None) -> int:
        """Подсчёт количества чатов."""
        query = select(func.count()).select_from(ChatSettingsModel)
        if filters:
            # Простая реализация фильтрации
            if filters.model_id is not None:
                query = query.where(ChatSettingsModel.model_id == filters.model_id)
            if filters.is_deleted is not None:
                query = query.where(ChatSettingsModel.deleted_at != None if not filters.is_deleted else ChatSettingsModel.deleted_at == None)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def count_sessions(self, chat_id: UUID) -> int:
        """Подсчёт количества сессий у чата."""
        result = await self.session.execute(
            select(func.count()).select_from(ChatSession).where(ChatSession.chat_id == chat_id)
        )
        return result.scalar() or 0
