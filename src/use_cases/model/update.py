from typing import Optional
"""
UseCase для обновления LLM модели.
"""

import logging
from typing import Optional

from src.domain.llm_model.models import LLMModel
from src.domain.llm_model.repositories import ModelRepositoryInterface
from src.exceptions.domain_exceptions import ModelNotFoundError
from src.use_cases.base_use_case import BaseUseCase
from src.use_cases.dto import ModelDTO

logger = logging.getLogger(__name__)


class UpdateModelInput:
    """Входные данные для обновления модели."""
    model_id: int
    name: str | None = None
    provider_model: str | None = None
    active: bool | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    context_window: int | None = None
    description: str | None = None

    def __init__(
        self,
        model_id: int,
        name: str | None = None,
        provider_model: str | None = None,
        active: bool | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        context_window: int | None = None,
        description: str | None = None,
    ):
        self.model_id = model_id
        self.name = name
        self.provider_model = provider_model
        self.active = active
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.context_window = context_window
        self.description = description


class UpdateModelUseCase(BaseUseCase[UpdateModelInput, ModelDTO]):
    """UseCase для обновления LLM модели."""

    def __init__(self, repository: ModelRepositoryInterface):
        self.repository = repository

    async def _run_logic(self, input_data: UpdateModelInput) -> ModelDTO:
        """Обновление модели."""
        logger.info(f"Обновление модели ID: {input_data.model_id}")

        # Получаем модель
        model = await self.repository.get(input_data.model_id)
        if not model:
            raise ModelNotFoundError(model_id=input_data.model_id)

        # Обновляем поля
        if input_data.name is not None:
            model.name = input_data.name
        if input_data.provider_model is not None:
            model.provider_model = input_data.provider_model
        if input_data.active is not None:
            model.active = input_data.active
        if input_data.temperature is not None:
            model.temperature = input_data.temperature
        if input_data.max_tokens is not None:
            model.max_tokens = input_data.max_tokens
        if input_data.context_window is not None:
            model.context_window = input_data.context_window
        if input_data.description is not None:
            model.description = input_data.description

        # Сохраняем
        updated_model = await self.repository.update(model)
        logger.info(f"Модель ID={input_data.model_id} обновлена")

        return ModelDTO.from_orm(updated_model)
