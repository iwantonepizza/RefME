"""
Исключения типа "не найдено" (404).
"""

from uuid import UUID

from src.exceptions.domain_exceptions.base import DomainException


class NotFoundError(DomainException):
    """Сущность не найдена."""
    status_code = 404
    error_code = "NOT_FOUND"

    def __init__(self, entity_name: str, field_name: str, field_value: str | int | UUID):
        self.field_name = field_name
        self.field_value = field_value
        self.entity_name = entity_name
        self.message = (
            f"Сущность '{entity_name}' с полем '{field_name}' "
            f"и значением '{field_value}' не найдена"
        )
        super().__init__(self.message)


class TokenNotFoundError(NotFoundError):
    """Токен не найден."""

    def __init__(self, token_id: int | None = None):
        if token_id:
            super().__init__("Токен", "token_id", token_id)
        else:
            super().__init__("Токен", "token_id", "unknown")


class ChatNotFoundError(NotFoundError):
    """Чат не найден."""

    def __init__(self, chat_id: UUID | int):
        super().__init__("Чат", "chat_id", chat_id)


class SessionNotFoundError(NotFoundError):
    """Сессия не найдена."""

    def __init__(self, session_id: UUID | int):
        super().__init__("Сессия", "session_id", session_id)


class ModelNotFoundError(NotFoundError):
    """Модель не найдена."""

    def __init__(self, model_id: int):
        super().__init__("Модель", "model_id", model_id)
