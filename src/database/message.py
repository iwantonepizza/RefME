"""
ORM модель для сообщения.
"""

import uuid
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, Text, text as sa_text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base_model import Base
from src.core.constants import MessageStatus, Role


class ChatMessageDB(Base):
    __tablename__ = "chat_messages"

    # Используем PG_UUID для PostgreSQL
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID первичный ключ"
    )

    # Время обработки
    started_at: Mapped[datetime | None] = mapped_column(nullable=True, comment="Время начала обработки")
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True, comment="Время завершения обработки")

    # Статус: pending | processing | completed | failed
    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus),
        server_default=sa_text("'pending'"),
        nullable=False,
        comment="Статус обработки"
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("chat_sessions.id"),
        nullable=False,
        comment="ID сессии"
    )

    # Роль: system | user | assistant
    role: Mapped[Role] = mapped_column(
        Enum(Role),
        nullable=False,
        default=Role.USER,
        comment="Роль сообщения"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="Содержимое сообщения")

    created_at: Mapped[datetime] = mapped_column(
        server_default=sa_text("now()"),
        comment="Время создания"
    )
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True, comment="Время удаления (soft delete)")

    # Relationships будут добавлены отдельно


# Alias для обратной совместимости
ChatMessage = ChatMessageDB
