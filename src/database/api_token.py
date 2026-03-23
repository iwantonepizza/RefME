"""
ORM модель для API токена.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Integer, String, text as sa_text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base_model import Base


class APITokenDB(Base):
    __tablename__ = "api_token"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Первичный ключ")
    token: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
        comment="Значение токена"
    )
    active: Mapped[bool] = mapped_column(
        Boolean,
        server_default=sa_text("true"),
        nullable=False,
        comment="Активен ли токен"
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=sa_text("now()"),
        comment="Время создания"
    )
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True, comment="Время истечения")
    last_used_at: Mapped[datetime | None] = mapped_column(nullable=True, comment="Последнее использование")
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True, comment="Время удаления (soft delete)")

    # Отношения с cascade delete
    chats = relationship("ChatSettingsDB", backref="token", cascade="all, delete-orphan")


# Alias для обратной совместимости
APIToken = APITokenDB
