"""
Утилита для получения access токена от auth-сервиса.
"""

import httpx

# URL auth-сервиса для получения токена
AUTH_TOKEN_URL = "https://saas.blco.pro/auth/api/accounts/user/get_token"

# Тестовые учетные данные
TEST_USERNAME = "ilia"
TEST_PASSWORD = "ilia"

# CSRF токен (может потребоваться обновление если сервер отклонит запрос)
DEFAULT_CSRF_TOKEN = "GBc5TwGSP4DWrc26q10zmpX3KgyVGNbbdLJQJXlV1HJPSP3F2JCmwmlVkypIKxLw"


class AuthTokenError(Exception):
    """Ошибка получения токена авторизации."""
    pass


async def get_access_token(
    username: str = TEST_USERNAME,
    password: str = TEST_PASSWORD,
    csrf_token: str = DEFAULT_CSRF_TOKEN,
    auth_url: str = AUTH_TOKEN_URL,
) -> str:
    """
    Получение access токена от auth-сервиса.

    :param username: Имя пользователя
    :param password: Пароль
    :param csrf_token: CSRF токен
    :param auth_url: URL auth-сервиса
    :return: Access токен
    :raises AuthTokenError: Если не удалось получить токен
    """
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-CSRFTOKEN": csrf_token,
    }

    json_data = {
        "username": username,
        "password": password,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                auth_url,
                headers=headers,
                json=json_data,
            )
            response.raise_for_status()

            data = response.json()
            access_token = data.get("access")

            if not access_token:
                raise AuthTokenError("Access токен не найден в ответе сервера")

            return access_token

    except httpx.HTTPStatusError as e:
        raise AuthTokenError(f"HTTP ошибка при получении токена: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise AuthTokenError(f"Ошибка запроса к auth-сервису: {e}")
    except Exception as e:
        raise AuthTokenError(f"Неожиданная ошибка при получении токена: {e}")


def create_auth_headers(access_token: str) -> dict:
    """
    Создание заголовков для авторизованного запроса.

    :param access_token: Access токен
    :return: Словарь с заголовками
    """
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


async def get_auth_headers(
    username: str = TEST_USERNAME,
    password: str = TEST_PASSWORD,
    csrf_token: str = DEFAULT_CSRF_TOKEN,
) -> dict:
    """
    Получение заголовков для авторизованного запроса.

    :param username: Имя пользователя
    :param password: Пароль
    :param csrf_token: CSRF токен
    :return: Словарь с заголовками авторизации
    """
    access_token = await get_access_token(
        username=username,
        password=password,
        csrf_token=csrf_token,
    )
    return create_auth_headers(access_token)
