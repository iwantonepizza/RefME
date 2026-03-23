"""
ORM модель для сессии.
"""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, text as sa_text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base_model import Base


class ChatSessionDB(Base):
    __tablename__ = "chat_sessions"

    # Используем PG_UUID для PostgreSQL
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID первичный ключ"
    )

    token_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("api_token.token"),
        nullable=False,
        comment="ID токена (значение)"
    )
    chat_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("chat_settings.id"),
        nullable=False,
        comment="ID чата"
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=sa_text("now()"),
        comment="Время создания"
    )
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True, comment="Время удаления (soft delete)")

    # Relationships будут добавлены отдельно


# Alias для обратной совместимости
ChatSession = ChatSessionDB
