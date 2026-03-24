"""
Domain исключения.

Используются в domain слое и use cases для обозначения специфичных ошибок.
Глобальные обработчики преобразуют их в HTTP ответы.
"""

from src.exceptions.domain_exceptions.base import DomainException
from src.exceptions.domain_exceptions.not_found import (
    NotFoundError,
    TokenNotFoundError,
    ChatNotFoundError,
    SessionNotFoundError,
    ModelNotFoundError,
)
from src.exceptions.domain_exceptions.already_exists import (
    AlreadyExistsError,
    ModelAlreadyExistsError,
)
from src.exceptions.domain_exceptions.validation import (
    InvalidInputError,
    InvalidInputWithFieldError,
    SessionNotBoundToChatError,
    TooManyImagesError,
    InvalidRoleError,
    PromptTooLongError,
)
from src.exceptions.domain_exceptions.authorization import (
    TokenInvalidError,
    TokenInactiveError,
)
from src.exceptions.domain_exceptions.llm_provider import (
    LLMProviderError,
    LLMTimeoutError,
    NoAvailableProviderError,
)

__all__ = [
    # Base
    "DomainException",
    # Not Found (404)
    "NotFoundError",
    "TokenNotFoundError",
    "ChatNotFoundError",
    "SessionNotFoundError",
    "ModelNotFoundError",
    # Already Exists (409)
    "AlreadyExistsError",
    "ModelAlreadyExistsError",
    # Validation (400)
    "InvalidInputError",
    "InvalidInputWithFieldError",
    "SessionNotBoundToChatError",
    "TooManyImagesError",
    "InvalidRoleError",
    "PromptTooLongError",
    # Authorization (401/403)
    "TokenInvalidError",
    "TokenInactiveError",
    # LLM Provider (503)
    "LLMProviderError",
    "LLMTimeoutError",
    "NoAvailableProviderError",
]
