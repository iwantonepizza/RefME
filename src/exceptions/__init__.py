"""
Исключения и обработчики.
"""

from src.exceptions.domain_exceptions import (
    DomainException,
    NotFoundError,
    AlreadyExistsError,
    InvalidInputError,
    InvalidInputWithFieldError,
    TokenInvalidError,
    TokenInactiveError,
    TooManyImagesError,
    InvalidRoleError,
    PromptTooLongError,
    LLMProviderError,
    LLMTimeoutError,
    NoAvailableProviderError,
    TokenNotFoundError,
    ChatNotFoundError,
    SessionNotFoundError,
    ModelNotFoundError,
    ModelAlreadyExistsError,
)

from src.exceptions.exceptions import (
    AppException,
    AuthorizationError,
    InvalidTokenError,
    MissingTokenError,
    ValidationError,
    ConflictError,
    ModelInactiveError,
    ExternalServiceError,
    LLMServiceError,
    DatabaseError,
    RateLimitExceededError,
)

from src.exceptions.handlers import register_exception_handlers

__all__ = [
    # Domain исключения
    "DomainException",
    "NotFoundError",
    "AlreadyExistsError",
    "InvalidInputError",
    "InvalidInputWithFieldError",
    "TokenInvalidError",
    "TokenInactiveError",
    "TooManyImagesError",
    "InvalidRoleError",
    "PromptTooLongError",
    "LLMProviderError",
    "LLMTimeoutError",
    "NoAvailableProviderError",
    "TokenNotFoundError",
    "ChatNotFoundError",
    "SessionNotFoundError",
    "ModelNotFoundError",
    "ModelAlreadyExistsError",
    # App исключения
    "AppException",
    "AuthorizationError",
    "InvalidTokenError",
    "MissingTokenError",
    "ValidationError",
    "ConflictError",
    "ModelInactiveError",
    "ExternalServiceError",
    "LLMServiceError",
    "DatabaseError",
    "RateLimitExceededError",
    # Обработчики
    "register_exception_handlers",
]
