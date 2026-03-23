from typing import List
"""
Схемы для админского управления моделями.
"""

from pydantic import BaseModel, Field


class ModelCreateSchema(BaseModel):
    """Схема создания модели."""

    name: str = Field(..., description="Человекочитаемое название модели")
    provider_model: str = Field(..., description="Имя модели у провайдера (Ollama)")
    provider: str = Field(default="ollama", description="Провайдер: ollama или vllm")
    type: str = Field(default="text", description="Тип модели: text, image, audio, video, multimodal")
    active: bool = Field(default=True, description="Активна ли модель")
    max_tokens: int | None = Field(default=None, description="Максимум токенов для генерации")
    context_window: int | None = Field(default=None, description="Размер контекстного окна")
    temperature: float | None = Field(default=0.7, description="Температура по умолчанию")
    description: str | None = Field(default=None, description="Описание модели")


class ModelUpdateSchema(BaseModel):
    """Схема обновления модели."""

    name: str | None = Field(default=None, description="Человекочитаемое название модели")
    provider_model: str | None = Field(default=None, description="Имя модели у провайдера")
    active: bool | None = Field(default=None, description="Активна ли модель")
    max_tokens: int | None = Field(default=None, description="Максимум токенов для генерации")
    context_window: int | None = Field(default=None, description="Размер контекстного окна")
    temperature: float | None = Field(default=None, description="Температура по умолчанию")
    description: str | None = Field(default=None, description="Описание модели")
