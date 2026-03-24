"""
Domain модель сообщения для LLM.
"""

from dataclasses import dataclass, field
from typing import List

from src.core.constants import Role


@dataclass
class LLMMessage:
    """Бизнес-объект сообщения для LLM."""
    role: Role  # "user", "assistant", "system"
    content: str  # Текстовое содержимое
    images: List[str] | None = None  # Base64 изображения (опционально)

    def to_dict(self) -> dict:
        """Конвертация в dict для отправки в LLM provider."""
        result = {"role": self.role.value, "content": self.content}
        if self.images:
            result["images"] = self.images
        return result
