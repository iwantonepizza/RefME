"""
Rate limiting middleware для LLM Gateway.
Использует SlowAPI для ограничения количества запросов.
"""

from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.core.config import settings

# Создаем лимитер с использованием remote address для идентификации клиентов
limiter = Limiter(key_func=get_remote_address)


class RateLimitSettings:
    """Настройки rate limiting из переменных окружения."""

    # Запросов в минуту для LLM эндпоинтов
    LLM_REQUESTS_PER_MINUTE = getattr(settings, "LLM_RATE_LIMIT", 60)

    # Запросов в минуту для админских эндпоинтов
    ADMIN_REQUESTS_PER_MINUTE = getattr(settings, "ADMIN_RATE_LIMIT", 30)

    # Запросов в минуту для токенов/чатов/сессий
    DEFAULT_REQUESTS_PER_MINUTE = getattr(settings, "DEFAULT_RATE_LIMIT", 100)


def get_client_ip(request: Request) -> str:
    """
    Получение реального IP адреса клиента с учётом прокси.
    """
    # Проверяем заголовки от прокси
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Берем первый IP из списка (оригинальный клиент)
        return forwarded_for.split(",")[0].strip()

    # Проверяем X-Real-IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # fallback на remote address
    return get_remote_address()


# Переопределяем key_func для использования заголовков прокси
limiter.key_func = get_client_ip


def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded) -> dict:
    """
    Обработчик превышения rate limit.
    Возвращает понятное сообщение об ошибке.
    """
    return {
        "detail": {
            "error": "rate_limit_exceeded",
            "message": f"Превышен лимит запросов. Попробуйте позже.",
            "limit": str(exc.detail),
        }
    }, 429


# Экспортируем лимитер для использования в main.py
