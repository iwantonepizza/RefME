"""
Кастомные исключения приложения.

AppException и производные — для общих ошибок приложения.
Domain исключения (NotFoundError и др.) находятся в domain_exceptions.py
"""


class AppException(Exception):
    """Базовое исключение приложения."""

    def __init__(self, message: str, status_code: int = 500, error_code: str = "app_error"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


# ==================== Ошибки авторизации (4xx) ====================


class AuthorizationError(AppException):
    """Базовая ошибка авторизации."""

    def __init__(self, message: str = "Ошибка авторизации", status_code: int = 401):
        super().__init__(message, status_code=status_code, error_code="authorization_error")


class TokenInactiveError(AuthorizationError):
    """Токен не активен."""

    def __init__(self):
        super().__init__("Токен не активен", status_code=403)


class InvalidTokenError(AuthorizationError):
    """Неверный токен."""

    def __init__(self, message: str = "Неверный токен"):
        super().__init__(message, status_code=401)


class MissingTokenError(AuthorizationError):
    """Токен отсутствует."""

    def __init__(self):
        super().__init__("Токен отсутствует", status_code=401)


# ==================== Ошибки валидации (4xx) ====================


class ValidationError(AppException):
    """Ошибка валидации данных."""

    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message, status_code=400, error_code="validation_error")


# ==================== Ошибки состояния (4xx) ====================


class ConflictError(AppException):
    """Конфликт состояния (409)."""

    def __init__(self, message: str):
        super().__init__(message, status_code=409, error_code="conflict_error")


class ModelAlreadyExistsError(ConflictError):
    """Модель уже существует."""

    def __init__(self, model_name: str):
        super().__init__(f"Модель {model_name} уже существует")


class ModelInactiveError(AppException):
    """Модель не активна."""

    def __init__(self, model_name: str):
        super().__init__(f"Модель {model_name} не активна", status_code=400, error_code="model_inactive")


# ==================== Ошибки внешних сервисов (5xx) ====================


class ExternalServiceError(AppException):
    """Ошибка внешнего сервиса."""

    def __init__(self, service_name: str, message: str | None = None):
        msg = message or f"Ошибка сервиса {service_name}"
        super().__init__(msg, status_code=503, error_code="external_service_error")


class LLMServiceError(ExternalServiceError):
    """Ошибка LLM сервиса."""

    def __init__(self, message: str | None = None):
        super().__init__("LLM", message or "Ошибка LLM сервиса")


class DatabaseError(AppException):
    """Ошибка базы данных."""

    def __init__(self, message: str | None = None):
        super().__init__(message or "Ошибка базы данных", status_code=500, error_code="database_error")


# ==================== Ошибки rate limiting (4xx) ====================


class RateLimitExceededError(AppException):
    """Превышен лимит запросов."""

    def __init__(self, limit: str):
        super().__init__(f"Превышен лимит запросов. Лимит: {limit}", status_code=429, error_code="rate_limit_exceeded")

