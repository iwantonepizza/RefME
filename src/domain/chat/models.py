"""
Domain модель чата.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Chat:
    """Бизнес-объект чата."""
    token_id: int  # Обязательное поле — ID токена владельца
    chat_id: UUID = field(default_factory=uuid4)  # Генерируется автоматически
    model_id: int | None = None
    model_name: str | None = None
    name: str | None = None
    system_prompt: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    context_window: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def __post_init__(self):
        """Валидация при создании."""
        if self.name and len(self.name) > 100:
            raise ValueError("Chat name too long (max 100 chars)")

        if self.system_prompt and len(self.system_prompt) > 32000:
            raise ValueError("System prompt too long (max 32000 chars)")

        if self.temperature is not None and not (0.0 <= self.temperature <= 2.0):
            raise ValueError("Temperature must be 0.0-2.0")

        # Проверяем max_tokens только если он установлен и не None
        if self.max_tokens is not None and self.max_tokens != 0 and not (1 <= self.max_tokens <= 32768):
            raise ValueError("max_tokens must be 1-32768")

        # Проверяем context_window только если он установлен и не None  
        if self.context_window is not None and self.context_window != 0 and not (512 <= self.context_window <= 131072):
            raise ValueError("context_window must be 512-131072")
