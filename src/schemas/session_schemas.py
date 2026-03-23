"""
Схемы для сессий.
"""

from uuid import UUID

from pydantic import BaseModel, Field


class SessionCreateSchema(BaseModel):
    """Схема создания сессии."""

    chat_id: UUID = Field(..., description="ID чата для привязки")
