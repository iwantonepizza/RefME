"""
Исключения LLM провайдера (503).
"""

from src.exceptions.domain_exceptions.base import DomainException


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
