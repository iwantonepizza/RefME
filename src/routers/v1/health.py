"""
Health check endpoint для мониторинга.
"""

import httpx
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select

from src.core.config import settings
from src.core.database import get_async_session
from src.core.rate_limiter import limiter
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    tags=["Health"],
)


@router.get("/health", tags=["Health"])
@limiter.limit("10/minute")  # Ограничение частоты запросов для защиты от abuse
async def health_check(request: Request, db: AsyncSession = Depends(get_async_session)) -> dict:
    """
    Проверка здоровья сервиса.

    Проверяет:
    - Статус приложения
    - Подключение к базе данных
    - Доступность Ollama сервиса
    """
    health = {
        "status": "healthy",
        "version": "1.0.1",
        "checks": {
            "database": {"status": "unknown", "message": ""},
            "ollama": {"status": "unknown", "message": ""},
        },
    }

    # Проверка БД
    try:
        await db.execute(select(1))
        health["checks"]["database"] = {"status": "ok", "message": "Database connection active"}
    except Exception as e:
        health["checks"]["database"] = {"status": "error", "message": str(e)}
        health["status"] = "unhealthy"

    # Проверка Ollama
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_URL}/api/tags")
            response.raise_for_status()
        health["checks"]["ollama"] = {"status": "ok", "message": "Ollama service available"}
    except httpx.TimeoutException:
        health["checks"]["ollama"] = {"status": "error", "message": "Connection timeout"}
        health["status"] = "degraded"
    except Exception as e:
        health["checks"]["ollama"] = {"status": "error", "message": str(e)}
        health["status"] = "degraded"

    return health

