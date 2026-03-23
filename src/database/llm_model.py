"""
ORM модель для LLM модели.
"""

from datetime import datetime

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, JSON, String, Text, text as sa_text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base_model import Base
from src.core.constants import ModelType, ProviderType


class LLMModelDB(Base):
    __tablename__ = "llm_models"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Первичный ключ")

    # Человекочитаемое имя (ограничение 255 символов)
    name: Mapped[str] = mapped_column(
        String(length=255),
        nullable=False,
        comment="Название модели"
    )

    # ID модели у провайдера (например: "llama2", "mistral", "gpt-4")
    # Это динамическое значение — идентификатор модели в системе провайдера
    provider_model: Mapped[str] = mapped_column(
        String,
        unique=False,
        index=True,
        nullable=False,
        comment="ID модели у провайдера"
    )

    # Типы поддерживаемого контента: ["text"], ["image"], ["text", "image"]
    # JSON массив строк, допустимые значения: "text", "image", "audio", "video", "multimodal"
    types: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        server_default='["text"]',
        comment="Типы контента"
    )

    # Провайдер: ollama | vllm
    provider: Mapped[ProviderType] = mapped_column(
        Enum(ProviderType),
        nullable=False,
        default=ProviderType.OLLAMA,
        comment="Провайдер модели"
    )

    # Статус модели
    active: Mapped[bool] = mapped_column(
        Boolean,
        server_default=sa_text("true"),
        nullable=False,
        comment="Активна ли модель"
    )

    # Настройки модели
    temperature: Mapped[float | None] = mapped_column(
        Float,
        server_default=sa_text("0.7"),
        nullable=True,
        comment="Температура по умолчанию"
    )
    max_tokens: Mapped[int | None] = mapped_column(nullable=True, comment="Максимум токенов")
    context_window: Mapped[int | None] = mapped_column(nullable=True, comment="Размер контекста")

    # Поддерживаемые форматы
    supported_formats: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="Поддерживаемые форматы")

    # Описание
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Описание модели")

    created_at: Mapped[datetime] = mapped_column(
        server_default=sa_text("now()"),
        comment="Время создания"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        server_default=sa_text("now()"),
        onupdate=sa_text("now()"),
        comment="Время последнего обновления"
    )
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True, comment="Время удаления (soft delete)")

    # Отношения
    chats = relationship("ChatSettingsDB", back_populates="model", lazy="select")


# Alias для обратной совместимости
LLMModel = LLMModelDB
