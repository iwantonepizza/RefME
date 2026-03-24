"""
UseCase для удаления LLM модели.
"""

import logging

from src.domain.llm_model.repositories import ModelRepository
from src.exceptions.domain_exceptions import ModelNotFoundError
from src.use_cases.base_use_case import BaseUseCase

logger = logging.getLogger(__name__)


class DeleteModelInput:
    """Входные данные для удаления модели."""
    model_id: int

    def __init__(self, model_id: int):
        self.model_id = model_id


class DeleteModelOutput:
    """Результат удаления модели."""
    success: bool

    def __init__(self, success: bool):
        self.success = success


class DeleteModelUseCase(BaseUseCase[DeleteModelInput, DeleteModelOutput]):
    """UseCase для удаления LLM модели (мягкое удаление)."""

    def __init__(self, repository: ModelRepository):
        self.repository = repository

    async def _run_logic(self, input_data: DeleteModelInput) -> DeleteModelOutput:
        """Удаление модели (мягкое - через active=False)."""
        logger.info(f"Удаление модели ID: {input_data.model_id}")

        # Получаем модель для проверки существования
        model = await self.repository.get_by_id(input_data.model_id)
        if not model:
            raise ModelNotFoundError(model_id=input_data.model_id)

        # Мягкое удаление - устанавливаем active=False
        model.active = False
        await self.repository.update(model)
        logger.info(f"Модель ID={input_data.model_id} удалена (мягкое удаление)")

        return DeleteModelOutput(success=True)
