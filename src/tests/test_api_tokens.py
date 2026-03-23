"""
Тесты для API токенов (routers/api_tokens.py).
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.api_token import APIToken


class TestApiTokens:
    """Тесты для эндпоинтов API токенов."""

    @pytest.mark.asyncio
    async def test_create_token(self, client: AsyncClient, headers_with_auth: dict):
        """Тест создания токена."""
        response = await client.post("/models/tokens/create", headers=headers_with_auth)

        assert response.status_code == 200
        data = response.json()
        assert "token_value" in data
        assert "token_id" in data
        assert len(data["token_value"]) == 64  # hex(32 bytes) = 64 chars

    @pytest.mark.asyncio
    async def test_get_all_tokens(self, client: AsyncClient, headers_with_auth: dict):
        """Тест получения всех токенов - базовая проверка."""
        response = await client.get("/models/tokens/", headers=headers_with_auth)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "pagination" in data
        assert "total" in data["pagination"]
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_update_token_activate(
        self, client: AsyncClient, headers_with_auth: dict, test_token_inactive: APIToken
    ):
        """Тест включения токена через update."""
        response = await client.put(f"/models/tokens/{test_token_inactive.id}?active=True", headers=headers_with_auth)

        assert response.status_code == 200
        data = response.json()
        assert data["active"] is True

    @pytest.mark.asyncio
    async def test_update_token_deactivate(self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken):
        """Тест выключения токена через update."""
        response = await client.put(f"/models/tokens/{test_token.id}?active=False", headers=headers_with_auth)

        assert response.status_code == 200
        data = response.json()
        assert data["active"] is False

    @pytest.mark.asyncio
    async def test_delete_token(self, client: AsyncClient, headers_with_auth: dict, test_db: AsyncSession):
        """Тест удаления токена."""
        # Создаем токен для удаления
        token = APIToken(token="to_delete_token", active=True)
        test_db.add(token)
        await test_db.commit()
        await test_db.refresh(token)

        response = await client.delete(f"/models/tokens/{token.id}", headers=headers_with_auth)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

        # Проверяем что токен удален
        result = await test_db.execute(select(APIToken).where(APIToken.id == token.id))
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_get_token_by_id(self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken):
        """Тест получения токена по ID."""
        response = await client.get(f"/models/tokens/{test_token.id}", headers=headers_with_auth)

        assert response.status_code == 200
        data = response.json()
        assert data["token_id"] == test_token.id
        assert data["token_value"] == test_token.token

    @pytest.mark.asyncio
    async def test_delete_nonexistent_token(self, client: AsyncClient, headers_with_auth: dict):
        """Тест удаления несуществующего токена."""
        response = await client.delete("/models/tokens/99999", headers=headers_with_auth)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_token_without_auth(self, client: AsyncClient):
        """Тест создания токена без авторизации."""
        response = await client.post("/models/tokens/create")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_tokens_without_auth(self, client: AsyncClient):
        """Тест получения токенов без авторизации."""
        response = await client.get("/models/tokens/")

        assert response.status_code == 401
