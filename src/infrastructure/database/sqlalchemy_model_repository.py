"""
Реализация репозитория для LLM моделей.
"""

from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import ModelType
from src.database.chat import ChatSettings
from src.database.llm_model import LLMModel as LLMModelORM, ModelType as ORMModelType
from src.domain.llm_model.models import LLMModel
from src.domain.llm_model.repositories import ModelRepository


class SqlAlchemyModelRepository(ModelRepository):
    """Репозиторий для LLM моделей на SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: LLMModelORM) -> LLMModel:
        """Преобразование ORM модели в Domain модель."""
        # Конвертируем types из ModelType enum в список строк
        types_list = []
        if model.types:
            if isinstance(model.types, list):
                types_list = [
                    t.value if isinstance(t, ModelType) else str(t)
                    for t in model.types
                ]
            elif isinstance(model.types, str):
                types_list = [model.types]
        
        return LLMModel(
            model_id=model.id,
            name=model.name,
            provider_model=model.provider_model,
            provider=model.provider,
            types=types_list,
            active=model.active,
            temperature=model.temperature,
            max_tokens=model.max_tokens,
            context_window=model.context_window,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    async def get_by_id(self, model_id: int) -> LLMModel | None:
        """Получение модели по ID с конвертацией в domain."""
        result = await self.session.execute(
            select(LLMModelORM).where(LLMModelORM.id == model_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list(
        self,
        active_only: bool = True,
        limit: int | None = None,
        offset: int | None = None,
        filters: dict | None = None,
    ) -> List[LLMModel]:
        """Получение списка моделей."""
        query = select(LLMModelORM)
        if active_only:
            query = query.where(LLMModelORM.active == True)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_by_provider_model(self, provider_model: str) -> LLMModel | None:
        """Получение модели по provider_model."""
        result = await self.session.execute(
            select(LLMModelORM).where(LLMModelORM.provider_model == provider_model)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def create(self, model: LLMModel) -> LLMModel:
        """Создание модели."""
        # Конвертируем types из списка строк в ModelType enum
        types_enum = []
        if model.types:
            types_enum = [ORMModelType(t) for t in model.types if t in [e.value for e in ORMModelType]]
        
        instance = LLMModelORM(
            name=model.name,
            provider_model=model.provider_model,
            provider=model.provider,
            types=types_enum,
            active=model.active,
            temperature=model.temperature,
            max_tokens=model.max_tokens,
            context_window=model.context_window,
            description=model.description,
        )
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return self._to_domain(instance)

    async def update(self, model: LLMModel) -> LLMModel | None:
        """Обновление модели."""
        result = await self.session.execute(
            select(LLMModelORM).where(LLMModelORM.id == model.model_id)
        )
        orm_model = result.scalar_one_or_none()
        if not orm_model:
            return None

        orm_model.name = model.name
        orm_model.provider_model = model.provider_model
        orm_model.provider = model.provider
        if model.types:
            orm_model.types = [ORMModelType(t) for t in model.types if t in [e.value for e in ORMModelType]]
        orm_model.active = model.active
        orm_model.temperature = model.temperature
        orm_model.max_tokens = model.max_tokens
        orm_model.context_window = model.context_window
        orm_model.description = model.description

        await self.session.flush()
        await self.session.refresh(orm_model)
        return self._to_domain(orm_model)

    async def delete(self, model_id: int) -> None:
        """Удаление модели."""
        result = await self.session.execute(
            select(LLMModelORM).where(LLMModelORM.id == model_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)

    async def count(self, filters: dict | None = None) -> int:
        """Подсчёт количества моделей."""
        query = select(func.count()).select_from(LLMModelORM)
        if filters:
            for field, value in filters.items():
                if value is not None:
                    query = query.where(getattr(LLMModelORM, field) == value)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_active_models(self) -> List[LLMModel]:
        """Получение всех активных моделей."""
        result = await self.session.execute(
            select(LLMModelORM).where(LLMModelORM.active == True)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]
