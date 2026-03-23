"""
E2E тесты для интеграционного тестирования с PostgreSQL.

Требуют запущенного PostgreSQL и применяют реальные миграции.
Запускаются отдельно от unit тестов.

Usage:
    pytest tests/test_e2e.py -v --e2e

Для запуска нужен запущенный PostgreSQL:
    docker-compose up -d db
"""

import os
import uuid
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from src.core.config import settings
from src.core.database import AsyncSessionLocal
from src.main import app
from src.tests.conftest import MOCK_AUTH_SERVICE_URL, MOCK_USER_ID


# Помечаем все тесты в файле как e2e
pytestmark = pytest.mark.e2e


@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для асинхронных тестов."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def e2e_client() -> AsyncGenerator[AsyncClient, None]:
    """
    HTTP клиент для E2E тестов с реальной БД.
    
    Использует settings.DATABASE_URL для подключения к PostgreSQL.
    """
    # Проверяем что переменная окружения установлена
    if not os.getenv("E2E_TESTS_ENABLED"):
        pytest.skip("E2E тесты не включены. Установите E2E_TESTS_ENABLED=1")
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture(scope="function")
async def e2e_headers(e2e_client: AsyncClient) -> dict:
    """Заголовки с авторизацией для E2E тестов."""
    return {
        "Authorization": f"Bearer mock_token_{uuid.uuid4()}",
        "Content-Type": "application/json",
    }


class TestE2EApiTokens:
    """E2E тесты для API токенов."""

    @pytest.mark.asyncio
    async def test_create_token(self, e2e_client: AsyncClient, e2e_headers: dict):
        """Тест создания API токена."""
        response = await e2e_client.post(
            "/models/tokens/create",
            headers=e2e_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "token" in data
        assert data["active"] is True

    @pytest.mark.asyncio
    async def test_list_tokens(self, e2e_client: AsyncClient, e2e_headers: dict):
        """Тест получения списка токенов."""
        # Сначала создадим токен
        create_response = await e2e_client.post(
            "/models/tokens/create",
            headers=e2e_headers,
        )
        assert create_response.status_code == 200
        
        # Получаем список
        response = await e2e_client.get(
            "/models/tokens/",
            headers=e2e_headers,
            params={"limit": 10, "offset": 0},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "pagination" in data
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_update_token(self, e2e_client: AsyncClient, e2e_headers: dict):
        """Тест обновления токена."""
        # Создаём токен
        create_response = await e2e_client.post(
            "/models/tokens/create",
            headers=e2e_headers,
        )
        token_id = create_response.json()["id"]
        
        # Обновляем
        response = await e2e_client.put(
            f"/models/tokens/{token_id}",
            headers=e2e_headers,
            params={"active": False},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["active"] is False

    @pytest.mark.asyncio
    async def test_delete_token(self, e2e_client: AsyncClient, e2e_headers: dict):
        """Тест удаления токена."""
        # Создаём токен
        create_response = await e2e_client.post(
            "/models/tokens/create",
            headers=e2e_headers,
        )
        token_id = create_response.json()["id"]
        
        # Удаляем
        response = await e2e_client.delete(
            f"/models/tokens/{token_id}",
            headers=e2e_headers,
        )
        
        assert response.status_code == 200
        
        # Проверяем что удалён
        get_response = await e2e_client.get(
            f"/models/tokens/{token_id}",
            headers=e2e_headers,
        )
        assert get_response.status_code == 404


class TestE2EChats:
    """E2E тесты для чатов."""

    @pytest.mark.asyncio
    async def test_create_chat(self, e2e_client: AsyncClient, e2e_headers: dict):
        """Тест создания чата."""
        # Создаём токен
        token_response = await e2e_client.post(
            "/models/tokens/create",
            headers=e2e_headers,
        )
        token_id = token_response.json()["id"]
        
        # Создаём чат
        response = await e2e_client.post(
            f"/models/tokens/{token_id}/chats/",
            headers=e2e_headers,
            json={
                "name": "E2E Test Chat",
                "system_prompt": "Test system prompt",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "E2E Test Chat"

    @pytest.mark.asyncio
    async def test_list_chats(self, e2e_client: AsyncClient, e2e_headers: dict):
        """Тест получения списка чатов."""
        # Создаём токен
        token_response = await e2e_client.post(
            "/models/tokens/create",
            headers=e2e_headers,
        )
        token_id = token_response.json()["id"]
        
        # Создаём чат
        await e2e_client.post(
            f"/models/tokens/{token_id}/chats/",
            headers=e2e_headers,
            json={"name": "Test Chat"},
        )
        
        # Получаем список
        response = await e2e_client.get(
            f"/models/tokens/{token_id}/chats/",
            headers=e2e_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1


class TestE2ESessions:
    """E2E тесты для сессий."""

    @pytest.mark.asyncio
    async def test_create_session(self, e2e_client: AsyncClient, e2e_headers: dict):
        """Тест создания сессии."""
        # Создаём токен
        token_response = await e2e_client.post(
            "/models/tokens/create",
            headers=e2e_headers,
        )
        token_id = token_response.json()["id"]
        
        # Создаём чат
        chat_response = await e2e_client.post(
            f"/models/tokens/{token_id}/chats/",
            headers=e2e_headers,
            json={"name": "Test Chat"},
        )
        chat_id = chat_response.json()["id"]
        
        # Создаём сессию
        response = await e2e_client.post(
            f"/models/tokens/{token_id}/sessions/create",
            headers=e2e_headers,
            params={"chat_id": chat_id},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data


class TestE2EAdminModels:
    """E2E тесты для админки моделей."""

    @pytest.mark.asyncio
    async def test_create_model(self, e2e_client: AsyncClient, e2e_headers: dict):
        """Тест создания модели."""
        response = await e2e_client.post(
            "/models/admin/models/",
            headers=e2e_headers,
            json={
                "name": "E2E Test Model",
                "provider_model": "test-model:7b",
                "type": "text",
                "active": True,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "E2E Test Model"
        assert data["provider_model"] == "test-model:7b"

    @pytest.mark.asyncio
    async def test_list_models(self, e2e_client: AsyncClient, e2e_headers: dict):
        """Тест получения списка моделей."""
        response = await e2e_client.get(
            "/models/admin/models/",
            headers=e2e_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "pagination" in data


class TestE2EHealth:
    """E2E тесты для health checks."""

    @pytest.mark.asyncio
    async def test_health_check(self, e2e_client: AsyncClient):
        """Тест проверки здоровья."""
        response = await e2e_client.get("/models/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"


@pytest.fixture(scope="session")
def db_url() -> str:
    """Получение URL базы данных из настроек."""
    return settings.DATABASE_URL


def test_database_connection(db_url: str):
    """Тест подключения к базе данных."""
    # Импортируем здесь чтобы не ломало другие тесты
    import asyncio
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine
    
    async def check_connection():
        engine = create_async_engine(
            db_url.replace("postgresql+asyncpg", "postgresql"),
            echo=False,
        )
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            assert row[0] == 1
        await engine.dispose()
    
    asyncio.run(check_connection())
