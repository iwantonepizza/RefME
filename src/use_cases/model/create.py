"""
UseCase для создания LLM модели.
"""

import logging
from datetime import datetime, timezone
from typing import List

from src.domain.llm_model.models import LLMModel
from src.domain.llm_model.repositories import ModelRepository
from src.exceptions.domain_exceptions import ModelAlreadyExistsError
from src.use_cases.base_use_case import BaseUseCase

logger = logging.getLogger(__name__)


class CreateModelInput:
    """Входные данные для создания модели."""
    name: str
    provider_model: str
    types: List[str]
    provider: str = "ollama"
    active: bool = True
    temperature: float | None = 0.7
    max_tokens: int | None = None
    context_window: int | None = None
    description: str | None = None

    def __init__(
        self,
        name: str,
        provider_model: str,
        types: List[str],
        provider: str = "ollama",
        active: bool = True,
        temperature: float | None = 0.7,
        max_tokens: int | None = None,
        context_window: int | None = None,
        description: str | None = None,
    ):
        self.name = name
        self.provider_model = provider_model
        self.types = types
        self.provider = provider
        self.active = active
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.context_window = context_window
        self.description = description


class CreateModelOutput:
    """Результат создания модели."""
    id: int  # alias для model_id
    name: str
    provider_model: str
    provider: str
    type: str  # alias для types[0]
    active: bool
    temperature: float | None = None
    max_tokens: int | None = None
    context_window: int | None = None
    description: str | None = None
    chats_count: int = 0

    def __init__(
        self,
        model_id: int,
        name: str,
        provider_model: str,
        provider: str,
        types: List[str],
        active: bool,
        temperature: float | None = None,
        max_tokens: int | None = None,
        context_window: int | None = None,
        description: str | None = None,
        chats_count: int = 0,
    ):
        self.model_id = model_id  # Конвертируем model_id → model_id
        self.name = name
        self.provider_model = provider_model
        self.provider = provider
        self.types = types  # Конвертируем types → types
        self.active = active
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.context_window = context_window
        self.description = description
        self.chats_count = chats_count

    def model_dump(self) -> dict:
        """Конвертация в dict для сериализации."""
        return {
            "model_id": self.model_id,
            "name": self.name,
            "provider_model": self.provider_model,
            "provider": self.provider,
            "types": self.types,
            "active": self.active,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "context_window": self.context_window,
            "description": self.description,
            "chats_count": self.chats_count,
        }


class CreateModelUseCase(BaseUseCase[CreateModelInput, CreateModelOutput]):
    """UseCase для создания новой LLM модели."""

    def __init__(self, repository: ModelRepository):
        self.repository = repository

    async def _run_logic(self, input_data: CreateModelInput) -> CreateModelOutput:
        """Создание модели."""
        logger.info(f"Создание модели: {input_data.name} ({input_data.provider_model})")

        # Проверяем что provider_model уникален
        existing = await self.repository.get_by_provider_model(input_data.provider_model)
        if existing:
            raise ModelAlreadyExistsError(model_name=input_data.provider_model)

        # Создаём domain модель
        domain_model = LLMModel(
            name=input_data.name,
            provider_model=input_data.provider_model,
            provider=input_data.provider,
            types=input_data.types,
            active=input_data.active,
            temperature=input_data.temperature,
            max_tokens=input_data.max_tokens,
            context_window=input_data.context_window,
            description=input_data.description,
        )

        # Сохраняем через репозиторий
        created_model = await self.repository.create(domain_model)
        logger.info(f"Модель создана с ID: {created_model.model_id}")

        return CreateModelOutput(
            model_id=created_model.model_id,
            name=created_model.name,
            provider_model=created_model.provider_model,
            provider=created_model.provider,
            types=created_model.types,
            active=created_model.active,
            temperature=created_model.temperature,
            max_tokens=created_model.max_tokens,
            context_window=created_model.context_window,
            description=created_model.description,
            chats_count=0,
        )
