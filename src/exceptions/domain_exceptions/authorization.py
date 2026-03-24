"""
Исключения авторизации (401/403).
"""

from src.exceptions.domain_exceptions.base import DomainException


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
