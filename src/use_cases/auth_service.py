"""
Сервис для внешней авторизации пользователей.

Отвечает за валидацию user_api_token через внешний auth-сервис
с retry логикой и обработкой ошибок.
"""

import asyncio

import httpx

from src.exceptions.exceptions import AuthorizationError
from src.core.logging import logger


class AuthService:
    """Сервис для внешней авторизации пользователей."""

    def __init__(self, auth_url: str | None = None):
        self.auth_url = auth_url
        self.max_retries = 3
        self.base_timeout = 2  # секунды

    async def validate_user_token(
        self,
        user_api_token: str,
        internal_service_code: str = "models-service",
    ) -> int | None:
        """
        Валидация user_api_token через внешний сервис авторизации.

        :param user_api_token: Bearer токен пользователя
        :param internal_service_code: Код сервиса для авторизации
        :return: user_id или None если невалиден
        """
        logger.info(f"Валидация токена {user_api_token[:8]}... , auth_url={self.auth_url}")

        headers = {
            "Authorization": f"Bearer {user_api_token}",
            "Content-Type": "application/json",
        }
        json_data = {"internal_service_code": internal_service_code}

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.base_timeout) as client:
                    response = await client.post(
                        self.auth_url,
                        headers=headers,
                        json=json_data,
                    )
                    response.raise_for_status()

                    user_id = response.json()
                    logger.info(f"Токен {user_api_token[:8]}... валиден, user_id={user_id}")
                    return user_id

            except httpx.TimeoutException as e:
                logger.warning(f"Timeout (попытка {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    wait_time = self.base_timeout * (2**attempt)
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("Превышено количество попыток валидации")
                    return None

            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                logger.error(f"Ошибка валидации токена: {e}")
                return None

        return None
