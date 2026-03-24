"""
Domain исключения.

Используются в domain слое и use cases для обозначения специфичных ошибок.
Глобальные обработчики преобразуют их в HTTP ответы.
"""

from uuid import UUID


class DomainException(Exception):
    """
    Базовый класс для domain исключений.

    Все domain исключения наследуются от этого класса.
    Глобальные обработчики преобразуют их в HTTP ответы.
    """
    status_code: int = 500
    error_code: str = "DOMAIN_ERROR"

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


# ==================== Ошибки "не найдено" (404) ====================


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


# ==================== Ошибки "уже существует" (409) ====================


class AlreadyExistsError(DomainException):
    """Сущность уже существует."""
    status_code = 409
    error_code = "ALREADY_EXISTS"

    def __init__(self, entity_name: str, field_name: str, field_value: str | int):
        self.field_name = field_name
        self.field_value = field_value
        self.entity_name = entity_name
        self.message = (
            f"Сущность '{entity_name}' со значением '{field_value}' "
            f"поля '{field_name}' уже существует"
        )
        super().__init__(self.message)


class ModelAlreadyExistsError(AlreadyExistsError):
    """Модель уже существует."""
    
    def __init__(self, model_name: str):
        super().__init__("Модель", "name", model_name)


# ==================== Ошибки валидации (400) ====================


class IncorrectValueError(DomainException):
    """Неверное значение параметра."""
    status_code = 400
    error_code = "INCORRECT_VALUE"

    def __init__(self, entity_name: str, field_name: str, limitation: str):
        self.message = (
            f"Неверное значение для параметра '{field_name}' в сущности: "
            f"'{entity_name}'. {limitation}"
        )
        super().__init__(self.message)


class InvalidInputError(DomainException):
    """Неверные входные данные."""
    status_code = 400
    error_code = "INVALID_INPUT"

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class SessionNotBoundToChatError(DomainException):
    """Сессия не привязана к чату."""
    status_code = 400
    error_code = "SESSION_NOT_BOUND_TO_CHAT"

    def __init__(self, session_id: UUID | int):
        self.message = f"Session {session_id} is not bound to any chat"
        super().__init__(self.message)


class TooManyImagesError(IncorrectValueError):
    """Слишком много изображений."""
    
    def __init__(self, max_count: int):
        super().__init__(
            "LLM запрос",
            "images",
            f"Максимум: {max_count} изображений"
        )


class InvalidRoleError(IncorrectValueError):
    """Неверная роль сообщения."""
    
    def __init__(self, role: str):
        super().__init__(
            "Сообщение",
            "role",
            f"Допустимы: user, system. Получено: {role}"
        )


class PromptTooLongError(IncorrectValueError):
    """Промпт слишком длинный."""
    
    def __init__(self, max_length: int, actual_length: int):
        super().__init__(
            "Промпт",
            "content",
            f"Максимум: {max_length} символов. Получено: {actual_length}"
        )


# ==================== Ошибки авторизации (401/403) ====================


class TokenInvalidError(DomainException):
    """Токен невалиден."""
    status_code = 401
    error_code = "TOKEN_INVALID"

    def __init__(self, message: str = "Токен невалиден или истёк"):
        self.message = message
        super().__init__(self.message)


class TokenInactiveError(DomainException):
    """Токен не активен."""
    status_code = 403
    error_code = "TOKEN_INACTIVE"

    def __init__(self, message: str = "Токен не активен"):
        self.message = message
        super().__init__(self.message)


# ==================== Ошибки LLM провайдера (503) ====================


class LLMProviderError(DomainException):
    """Ошибка LLM провайдера."""
    status_code = 503
    error_code = "LLM_PROVIDER_UNAVAILABLE"

    def __init__(self, provider_name: str, message: str):
        self.provider_name = provider_name
        self.message = f"LLM провайдер '{provider_name}' недоступен: {message}"
        super().__init__(self.message)


class LLMTimeoutError(LLMProviderError):
    """Таймаут LLM провайдера."""
    
    def __init__(self, provider_name: str = "LLM"):
        super().__init__(provider_name, "Таймаут запроса")


class NoAvailableProviderError(DomainException):
    """Нет доступного провайдера."""
    status_code = 503
    error_code = "NO_AVAILABLE_PROVIDER"

    def __init__(self):
        self.message = "Нет доступного LLM провайдера"
        super().__init__(self.message)
