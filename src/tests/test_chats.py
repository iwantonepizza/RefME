"""
Тесты для управления чатами (routers/chats.py).
"""

from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.api_token import APIToken
from src.database.chat import ChatSettings


class TestChats:
    """Тесты для эндпоинтов чатов."""

    @pytest.mark.asyncio
    async def test_create_chat(self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken):
        """Тест создания чата."""
        response = await client.post(f"/models/tokens/{test_token.id}/chats/", headers=headers_with_auth)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["token_id"] == test_token.id

    @pytest.mark.asyncio
    async def test_list_chats(
        self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken, test_chat: ChatSettings
    ):
        """Тест получения списка чатов."""
        response = await client.get(f"/models/tokens/{test_token.id}/chats/", headers=headers_with_auth)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= 1

        chat_ids = [c["id"] for c in data["items"]]
        assert str(test_chat.id) in chat_ids

    @pytest.mark.asyncio
    async def test_get_chat(
        self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken, test_chat: ChatSettings
    ):
        """Тест получения чата."""
        response = await client.get(f"/models/tokens/{test_token.id}/chats/{test_chat.id}", headers=headers_with_auth)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_chat.id)
        assert data["token_id"] == test_token.id

    @pytest.mark.asyncio
    async def test_update_chat(
        self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken, test_chat: ChatSettings
    ):
        """Тест обновления чата."""
        update_data = {"name": "Updated Chat", "temperature": 0.5, "max_tokens": 2048}

        response = await client.put(
            f"/models/tokens/{test_token.id}/chats/{test_chat.id}", json=update_data, headers=headers_with_auth
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Chat"
        assert data["temperature"] == 0.5
        assert data["max_tokens"] == 2048

    @pytest.mark.asyncio
    async def test_delete_chat(
        self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken, test_db: AsyncSession
    ):
        """Тест удаления чата."""
        # Создаем чат для удаления
        chat = ChatSettings(token_id=test_token.id)
        test_db.add(chat)
        await test_db.commit()
        await test_db.refresh(chat)

        response = await client.delete(f"/models/tokens/{test_token.id}/chats/{chat.id}", headers=headers_with_auth)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_get_nonexistent_chat(self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken):
        """Тест получения несуществующего чата."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/models/tokens/{test_token.id}/chats/{fake_id}", headers=headers_with_auth)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_chat_for_inactive_token(
        self, client: AsyncClient, headers_with_auth: dict, test_token_inactive: APIToken
    ):
        """Тест создания чата для неактивного токена - чат создается, так как проверка только для LLM запросов."""
        response = await client.post(f"/models/tokens/{test_token_inactive.id}/chats/", headers=headers_with_auth)

        # Чат создается успешно, проверка активности только для LLM endpoints
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_chat_without_auth(self, client: AsyncClient, test_token: APIToken):
        """Тест создания чата без авторизации."""
        response = await client.post(f"/models/tokens/{test_token.id}/chats/")

        assert response.status_code == 401
