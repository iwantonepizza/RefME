"""
Главный роутер API v1.
"""

from fastapi import APIRouter

from src.routers.v1.api_tokens import router as api_tokens_router
from src.routers.v1.chats import router as chats_router
from src.routers.v1.sessions import router as sessions_router
from src.routers.v1.llm import router as llm_router
from src.routers.v1.health import router as health_router
from src.routers.admin import admin_router

# Создаём главный роутер с префиксом /models
api_router = APIRouter(prefix="/models")

# Регистрируем все роутеры
api_router.include_router(api_tokens_router, prefix="/tokens")
api_router.include_router(chats_router)
api_router.include_router(sessions_router)
api_router.include_router(llm_router)
api_router.include_router(health_router)
api_router.include_router(admin_router)

__all__ = ["api_router"]
