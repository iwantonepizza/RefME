"""
Утилиты для авторизации.

Обёртки для использования AuthService в FastAPI Depends.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.logging import logger
from src.use_cases.auth_service import AuthService
from src.use_cases.dependencies import get_auth_service

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> int | None:
    """
    Вытягивание токена из заголовка и авторизация через сервис авторизации.

    :param credentials: Данные авторизации
    :param auth_service: Сервис авторизации
    :return: user_id
    """
    logger.info("Вытягивание user_api_token из заголовка")

    if not credentials:
        logger.info("Попытка обращения без user_api_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = credentials.credentials

    logger.info(f"user_api_token получен {token[:8]}...")

    user_id = await auth_service.validate_user_token(token)

    if not user_id:
        logger.info("Попытка обращения с невалидным user_api_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user API token",
        )

    return user_id
