"""
Domain модель LLM модели.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class LLMModel:
    """Бизнес-объект LLM модели."""
    model_id: int = 0
    name: str = ""
    provider_model: str = ""
    provider: str = ""
    types: List[str] = field(default_factory=list)
    active: bool = True
    temperature: float | None = None
    max_tokens: int | None = None
    context_window: int | None = None
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
