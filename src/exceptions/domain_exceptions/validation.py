"""
Исключения валидации (400).
"""

from uuid import UUID
from typing import Any

from src.exceptions.domain_exceptions.base import DomainException


class InvalidInputError(DomainException):
    """
    Ошибка валидации входных данных.
    
    Примеры:
    - Некорректный формат поля
    - Значение вне допустимого диапазона
    - Обязательное поле отсутствует
    """
    status_code = 400
    error_code = "INVALID_INPUT"

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None
    ):
        self.field = field
        self.value = value
        self.message = message
        super().__init__(self.message)


class InvalidInputWithFieldError(InvalidInputError):
    """
    Ошибка валидации с указанием поля.
    
    Наследуется от InvalidInputError для обратной совместимости.
    """
    error_code = "INCORRECT_VALUE"
    
    def __init__(self, entity_name: str, field_name: str, limitation: str):
        message = (
            f"Неверное значение для параметра '{field_name}' в сущности: "
            f"'{entity_name}'. {limitation}"
        )
        super().__init__(message=message, field=field_name)


# ==================== Специфичные ошибки валидации ====================


class SessionNotBoundToChatError(InvalidInputError):
    """Сессия не привязана к чату."""
    status_code = 400
    error_code = "SESSION_NOT_BOUND_TO_CHAT"

    def __init__(self, session_id: UUID | int):
        super().__init__(f"Session {session_id} is not bound to any chat")


class TooManyImagesError(InvalidInputWithFieldError):
    """Слишком много изображений."""

    def __init__(self, max_count: int):
        super().__init__(
            entity_name="LLM запрос",
            field_name="images",
            limitation=f"Максимум: {max_count} изображений"
        )


class InvalidRoleError(InvalidInputWithFieldError):
    """Неверная роль сообщения."""

    def __init__(self, role: str):
        super().__init__(
            entity_name="Сообщение",
            field_name="role",
            limitation=f"Допустимы: user, system. Получено: {role}"
        )


class PromptTooLongError(InvalidInputWithFieldError):
    """Промпт слишком длинный."""

    def __init__(self, max_length: int, actual_length: int):
        super().__init__(
            entity_name="Промпт",
            field_name="content",
            limitation=f"Максимум: {max_length} символов. Получено: {actual_length}"
        )
