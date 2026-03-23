"""
Админские роутеры.
"""

from fastapi import APIRouter

from src.routers.admin.models import router as models_router
from src.routers.admin.ollama import router as control_router
from src.routers.admin.sessions import router as sessions_router

admin_router = APIRouter(prefix="/admin")

admin_router.include_router(models_router, prefix="/models", tags=["Admin Models"])
admin_router.include_router(sessions_router, prefix="/sessions", tags=["Admin Sessions"])
admin_router.include_router(control_router, prefix="/control", tags=["Admin Control"])
