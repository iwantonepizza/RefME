from typing import Any, Dict, List
"""
DTO для LLM use cases.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from fastapi import UploadFile


@dataclass
class LLMRequestInput:
    """Входные данные для запроса к LLM."""
    session_id: UUID
    msg_text: str | None = None
    role: str = "user"
    images: list[UploadFile] | None = None


@dataclass
class LLMRequestOutput:
    """Результат запроса к LLM."""
    response: str
    latency: float
    session_id: UUID


@dataclass
class LLMStreamInput:
    """Входные данные для стриминга LLM."""
    session_id: UUID
    msg_text: str | None = None
    role: str = "user"
    images: list[UploadFile] | None = None


@dataclass
class LLMSingleInput:
    """Входные данные для запроса к LLM без истории."""
    chat_id: UUID
    msg_text: str | None = None
    role: str = "user"
    images: list[UploadFile] | None = None


@dataclass
class LLMSingleOutput:
    """Результат запроса к LLM без истории."""
    response: str
    latency: float
    chat_id: UUID


@dataclass
class EffectiveSettings:
    """Эффективные настройки для LLM запроса."""
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    context_window: int = 4096


# Алиасы для обратной совместимости
LLMAskInput = LLMRequestInput
LLMAskOutput = LLMRequestOutput
