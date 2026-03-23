from typing import List, Optional
"""
Схемы для API токенов.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class TokenCreateSchema(BaseModel):
    """Схема создания токена (пустая, токен генерируется автоматически)."""

    pass


class TokenUpdateSchema(BaseModel):
    """Схема обновления токена."""

    active: bool = Field(..., description="True - включить, False - выключить")
