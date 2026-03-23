"""
Утилиты для работы с API токенами.

Обёртки для использования TokenRepository в FastAPI Depends.
"""

from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.exceptions.exceptions import InvalidTokenError, MissingTokenError
from src.core.logging import logger
from src.database.api_token import APIToken
from src.infrastructure.database.token_repository_impl import SqlAlchemyTokenRepository


async def get_llm_api_token_from_headers(
    api_llm_token: Optional[str] = Header(None, alias="api-token"),
    session: AsyncSession = Depends(get_async_session),
) -> APIToken:
    """
    Получение llm_api_token из заголовка.

    :param api_llm_token: Заголовок API-токена
    :param session: Сессия БД
    :return: Объект APIToken
    """
    if not api_llm_token:
        raise MissingTokenError()

    token_repository = SqlAlchemyTokenRepository(session)
    api_token = await token_repository.get_active_by_token_value(api_llm_token)

    if not api_token:
        raise InvalidTokenError()

    logger.debug(f"llm_api_token получен (ID: {api_token.token_id})")
    return api_token
