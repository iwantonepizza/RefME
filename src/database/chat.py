"""
ORM модель для чата.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, text as sa_text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base_model import Base


class ChatSettingsDB(Base):
    __tablename__ = "chat_settings"

    # Используем PG_UUID для PostgreSQL
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID первичный ключ"
    )

    token_id: Mapped[int] = mapped_column(
        ForeignKey("api_token.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID токена владельца"
    )
    model_id: Mapped[int | None] = mapped_column(
        ForeignKey("llm_models.id"),
        nullable=True,
        comment="ID модели из справочника"
    )
    model_name: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="Название модели (денормализация)"
    )

    name: Mapped[str | None] = mapped_column(nullable=True, comment="Название чата")
    system_prompt: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="Системный промпт для чата"
    )

    # Настройки чата
    temperature: Mapped[float | None] = mapped_column(nullable=True, comment="Температура генерации")
    max_tokens: Mapped[int | None] = mapped_column(nullable=True, comment="Максимум токенов")
    context_window: Mapped[int | None] = mapped_column(nullable=True, comment="Размер контекстного окна")

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
    model = relationship("LLMModelDB", back_populates="chats")


# Alias для обратной совместимости
ChatSettings = ChatSettingsDB
