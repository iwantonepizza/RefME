"""
UseCase для получения списка LLM моделей.
"""

from src.domain.llm_model.models import LLMModel
from src.domain.llm_model.repositories import ModelRepository
from src.use_cases.base_use_case import BaseUseCase
from src.use_cases.dto import ModelDTO, ModelListDTO, PaginationDTO


class ListModelsInput:
    """Входные данные для получения списка моделей."""
    active_only: bool = True
    limit: int | None = 100
    offset: int | None = 0

    def __init__(self, active_only: bool = True, limit: int | None = 100, offset: int | None = 0):
        self.active_only = active_only
        self.limit = limit
        self.offset = offset


class ListModelsUseCase(BaseUseCase[ListModelsInput, ModelListDTO]):
    """UseCase для получения списка LLM моделей."""

    def __init__(self, repository: ModelRepository):
        self.repository = repository

    async def _run_logic(self, input_data: ListModelsInput) -> ModelListDTO:
        """Получение списка моделей."""
        # Получаем список моделей
        models = await self.repository.list(
            active_only=input_data.active_only,
            limit=input_data.limit or 100,
            offset=input_data.offset or 0,
        )

        # Получаем общее количество
        total = await self.repository.count(
            filters={"active": True} if input_data.active_only else None
        )

        # Конвертируем в DTO
        items = [ModelDTO.model_validate(model) for model in models]

        return ModelListDTO(
            items=items,
            pagination=PaginationDTO(
                limit=input_data.limit or 100,
                offset=input_data.offset or 0,
                total=total,
            ),
        )
