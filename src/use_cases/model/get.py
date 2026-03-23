"""
UseCase для получения LLM модели по ID.
"""

from src.domain.llm_model.models import LLMModel
from src.domain.llm_model.repositories import ModelRepositoryInterface
from src.exceptions.domain_exceptions import ModelNotFoundError
from src.use_cases.base_use_case import BaseUseCase
from src.use_cases.dto import ModelDTO


class GetModelInput:
    """Входные данные для получения модели."""
    model_id: int

    def __init__(self, model_id: int):
        self.model_id = model_id


class GetModelUseCase(BaseUseCase[GetModelInput, ModelDTO]):
    """UseCase для получения LLM модели по ID."""

    def __init__(self, repository: ModelRepositoryInterface):
        self.repository = repository

    async def _run_logic(self, input_data: GetModelInput) -> ModelDTO:
        """Получение модели по ID."""
        model = await self.repository.get(input_data.model_id)

        if not model:
            raise ModelNotFoundError(model_id=input_data.model_id)

        return ModelDTO.from_orm(model)
