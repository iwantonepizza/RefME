"""
Тесты ошибок и edge cases для увеличения покрытия роутеров.
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.database.api_token import APIToken
from src.database.session import ChatSession
from src.database.chat import ChatSettings


class TestRouterErrorCases:
    """Тесты обработки ошибок в роутерах."""

    # ========== API Tokens Error Cases ==========

    @pytest.mark.asyncio
    async def test_update_nonexistent_token(self, client: AsyncClient, headers_with_auth: dict):
        """Тест обновления несуществующего токена."""
        response = await client.put("/models/tokens/99999?active=True", headers=headers_with_auth)
        # Обработчик исключений конвертирует TokenNotFoundError в 404
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_token(self, client: AsyncClient, headers_with_auth: dict):
        """Тест удаления несуществующего токена."""
        response = await client.delete("/models/tokens/99999", headers=headers_with_auth)
        assert response.status_code == 404

    # ========== Chats Error Cases ==========

    @pytest.mark.asyncio
    async def test_get_chat_nonexistent(self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken):
        """Тест получения несуществующего чата."""
        fake_id = str(uuid4())
        response = await client.get(f"/models/tokens/{test_token.id}/chats/{fake_id}", headers=headers_with_auth)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_chat_nonexistent(self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken):
        """Тест обновления несуществующего чата."""
        fake_id = str(uuid4())
        response = await client.put(
            f"/models/tokens/{test_token.id}/chats/{fake_id}", json={"name": "Test"}, headers=headers_with_auth
        )
        # Обработчик исключений конвертирует ChatNotFoundError в 404
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_chat_nonexistent(self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken):
        """Тест удаления несуществующего чата."""
        fake_id = str(uuid4())
        response = await client.delete(f"/models/tokens/{test_token.id}/chats/{fake_id}", headers=headers_with_auth)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_chat_inactive_token(
        self, client: AsyncClient, headers_with_auth: dict, test_token_inactive: APIToken
    ):
        """Тест создания чата с неактивным токеном - чат создается, проверка только для LLM."""
        response = await client.post(f"/models/tokens/{test_token_inactive.id}/chats/", headers=headers_with_auth)
        # Проверка активности только для LLM endpoints
        assert response.status_code == 200

    # ========== Sessions Error Cases ==========

    @pytest.mark.asyncio
    async def test_create_session_nonexistent_chat(
        self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken
    ):
        """Тест создания сессии с несуществующим чатом."""
        fake_id = str(uuid4())
        response = await client.post(
            f"/models/tokens/{test_token.id}/sessions/create", params={"chat_id": fake_id}, headers=headers_with_auth
        )
        # Сессия создается успешно (проверка чата не строгая)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_session_nonexistent(self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken):
        """Тест получения несуществующей сессии."""
        fake_id = str(uuid4())
        response = await client.get(f"/models/tokens/{test_token.id}/sessions/{fake_id}", headers=headers_with_auth)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_messages_nonexistent_session(
        self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken
    ):
        """Тест получения сообщений несуществующей сессии."""
        fake_id = str(uuid4())
        response = await client.get(
            f"/models/tokens/{test_token.id}/sessions/{fake_id}/messages",
            headers=headers_with_auth,
        )
        # Возвращает пустой список
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_session_nonexistent(self, client: AsyncClient, headers_with_auth: dict, test_token: APIToken):
        """Тест удаления несуществующей сессии."""
        fake_id = str(uuid4())
        response = await client.delete(f"/models/tokens/{test_token.id}/sessions/{fake_id}", headers=headers_with_auth)
        assert response.status_code == 404

    # ========== Admin Sessions Error Cases ==========

    @pytest.mark.asyncio
    async def test_admin_get_nonexistent_session(self, client: AsyncClient, headers_with_auth: dict):
        """Тест получения несуществующей сессии админом."""
        fake_id = str(uuid4())
        response = await client.get(f"/models/admin/sessions/{fake_id}", headers=headers_with_auth)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_admin_get_nonexistent_token(self, client: AsyncClient, headers_with_auth: dict):
        """Тест получения сессий несуществующего токена админом."""
        response = await client.get("/models/admin/sessions/token/99999", headers=headers_with_auth)
        assert response.status_code == 200  # Вернёт пустой список

    @pytest.mark.asyncio
    async def test_admin_get_nonexistent_chat(self, client: AsyncClient, headers_with_auth: dict):
        """Тест получения сессий несуществующего чата админом."""
        fake_id = str(uuid4())
        response = await client.get(f"/models/admin/sessions/chat/{fake_id}", headers=headers_with_auth)
        # Админский роутер просто возвращает пустой список если чат не найден
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 0

    @pytest.mark.asyncio
    async def test_admin_delete_nonexistent_session(self, client: AsyncClient, headers_with_auth: dict):
        """Тест удаления несуществующей сессии админом."""
        fake_id = str(uuid4())
        response = await client.delete(f"/models/admin/sessions/{fake_id}", headers=headers_with_auth)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_admin_get_messages_nonexistent_session(self, client: AsyncClient, headers_with_auth: dict):
        """Тест получения сообщений несуществующей сессии админом."""
        fake_id = str(uuid4())
        response = await client.get(f"/models/admin/sessions/{fake_id}/messages", headers=headers_with_auth)
        # Возвращает пустой список с pagination
        assert response.status_code == 200
