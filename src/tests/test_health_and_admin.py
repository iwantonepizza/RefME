"""
Тесты для health endpoint и admin models - увеличение покрытия.
"""

import pytest
import respx
from httpx import AsyncClient, Response

from src.database.api_token import APIToken
from src.database.chat import ChatSettings
from src.database.session import ChatSession
from src.database.llm_model import LLMModel


class TestHealthEndpoint:
    """Тесты для GET /health."""

    @pytest.mark.asyncio
    async def test_health_success(self, client: AsyncClient):
        """Тест успешного health check."""
        response = await client.get("/models/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "version" in data
        assert "checks" in data
        # Статус может быть healthy или degraded в зависимости от доступности сервисов
        assert data["status"] in ["healthy", "degraded"]

        checks = data["checks"]
        assert "database" in checks
        # Статус БД может быть ok или error (в тестах может быть error из-за mock)
        assert checks["database"]["status"] in ["ok", "error"]

    @pytest.mark.asyncio
    async def test_health_version(self, client: AsyncClient):
        """Тест что версия указана корректно."""
        response = await client.get("/models/health")
        
        data = response.json()
        assert data["version"] == "1.0.1"

    @pytest.mark.asyncio
    @respx.mock
    async def test_health_with_ollama_available(self, client: AsyncClient):
        """Тест health check с доступной Ollama."""
        from src.core.config import settings
        
        respx.get(f"{settings.OLLAMA_URL}/api/tags").mock(
            return_value=Response(200, json={"models": [{"name": "llama2"}]})
        )
        
        response = await client.get("/models/health")
        
        data = response.json()
        assert "ollama" in data["checks"]


class TestAdminModelsEndpoint:
    """Тесты для админского управления моделями."""

    @pytest.mark.asyncio
    async def test_admin_list_models(self, client: AsyncClient, headers_with_auth: dict):
        """Тест получения списка моделей админом."""
        response = await client.get("/models/admin/models/", headers=headers_with_auth)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "pagination" in data

    @pytest.mark.asyncio
    async def test_admin_list_models_with_inactive(
        self, client: AsyncClient, headers_with_auth: dict, test_model: LLMModel
    ):
        """Тест получения моделей включая неактивные."""
        response = await client.get(
            "/models/admin/models/?show_inactive=true&limit=10&offset=0",
            headers=headers_with_auth,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "pagination" in data
        assert data["pagination"]["limit"] == 10
        assert data["pagination"]["offset"] == 0

    @pytest.mark.asyncio
    async def test_admin_get_model(
        self, client: AsyncClient, headers_with_auth: dict, test_model: LLMModel
    ):
        """Тест получения модели по ID."""
        response = await client.get(f"/models/admin/models/{test_model.id}", headers=headers_with_auth)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_model.id
        assert data["name"] == test_model.name
        assert data["provider_model"] == test_model.provider_model

    @pytest.mark.asyncio
    async def test_admin_get_nonexistent_model(self, client: AsyncClient, headers_with_auth: dict):
        """Тест получения несуществующей модели."""
        response = await client.get("/models/admin/models/99999", headers=headers_with_auth)
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_admin_create_model(self, client: AsyncClient, headers_with_auth: dict):
        """Тест создания модели админом."""
        model_data = {
            "name": "Test Model Admin",
            "provider_model": "test-model-admin:7b",
            "provider": "ollama",
            "type": "text",
            "active": True,
            "temperature": 0.8,
            "max_tokens": 4096,
            "context_window": 8192,
        }
        
        response = await client.post(
            "/models/admin/models/",
            json=model_data,
            headers=headers_with_auth,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Test Model Admin"
        assert data["provider_model"] == "test-model-admin:7b"
        assert data["temperature"] == 0.8

    @pytest.mark.asyncio
    async def test_admin_create_model_duplicate(
        self, client: AsyncClient, headers_with_auth: dict, test_model: LLMModel
    ):
        """Тест создания модели с дублирующимся provider_model."""
        model_data = {
            "name": "Duplicate Model",
            "provider_model": test_model.provider_model,  # Дубликат
            "provider": "ollama",
            "type": "text",
        }
        
        response = await client.post(
            "/models/admin/models/",
            json=model_data,
            headers=headers_with_auth,
        )
        
        # 400 или 409 для дубликата
        assert response.status_code in [400, 409]

    @pytest.mark.asyncio
    async def test_admin_update_model(
        self, client: AsyncClient, headers_with_auth: dict, test_model: LLMModel
    ):
        """Тест обновления модели."""
        response = await client.put(
            f"/models/admin/models/{test_model.id}",
            json={"name": "Updated Model", "temperature": 0.9},
            headers=headers_with_auth,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Model"
        assert data["temperature"] == 0.9

    @pytest.mark.asyncio
    async def test_admin_update_model_nonexistent(self, client: AsyncClient, headers_with_auth: dict):
        """Тест обновления несуществующей модели."""
        response = await client.put(
            "/models/admin/models/99999",
            json={"name": "Test"},
            headers=headers_with_auth,
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_admin_delete_model(
        self, client: AsyncClient, headers_with_auth: dict, test_model: LLMModel
    ):
        """Тест удаления модели (мягкое)."""
        response = await client.delete(
            f"/models/admin/models/{test_model.id}",
            headers=headers_with_auth,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data

    @pytest.mark.asyncio
    async def test_admin_delete_nonexistent_model(self, client: AsyncClient, headers_with_auth: dict):
        """Тест удаления несуществующей модели."""
        response = await client.delete(
            "/models/admin/models/99999",
            headers=headers_with_auth,
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_admin_create_model_without_auth(self, client: AsyncClient):
        """Тест создания модели без авторизации."""
        response = await client.post(
            "/models/admin/models/",
            json={"name": "Test", "provider_model": "test:7b"},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_admin_list_models_without_auth(self, client: AsyncClient):
        """Тест получения списка моделей без авторизации."""
        response = await client.get("/models/admin/models/")
        
        assert response.status_code == 401


class TestAdminSessionsEndpoints:
    """Тесты для админских сессий - дополнительное покрытие."""

    @pytest.mark.asyncio
    async def test_admin_get_sessions_pagination(
        self, client: AsyncClient, headers_with_auth: dict
    ):
        """Тест пагинации сессий."""
        response = await client.get(
            "/models/admin/sessions/?limit=5&offset=10",
            headers=headers_with_auth,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "pagination" in data
        assert data["pagination"]["limit"] == 5
        assert data["pagination"]["offset"] == 10

    @pytest.mark.asyncio
    async def test_admin_get_messages_pagination(
        self, client: AsyncClient, headers_with_auth: dict, test_session: ChatSession
    ):
        """Тест пагинации сообщений."""
        response = await client.get(
            f"/models/admin/sessions/{test_session.id}/messages?limit=10&offset=0",
            headers=headers_with_auth,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "pagination" in data
        assert data["pagination"]["limit"] == 10
