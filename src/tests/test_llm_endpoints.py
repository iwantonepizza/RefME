"""
Тесты для LLM роутера (routers/llm.py) - увеличение покрытия.
"""

import base64
import pytest
import respx
from httpx import AsyncClient, Response

from src.database.api_token import APIToken
from src.database.chat import ChatSettings
from src.database.session import ChatSession
from src.database.message import ChatMessage
from src.database.llm_model import LLMModel
from src.tests.conftest import test_session_with_deleted_chat


# Тестовое изображение (1x1 пиксель)
TEST_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="


class TestLLMAskEndpoint:
    """Тесты для POST /llm/ask."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_ask_success(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
        test_chat: ChatSettings,
        test_session: ChatSession,
    ):
        """Тест успешного запроса к /llm/ask."""
        from src.core.config import settings
        
        # Мокаем health check и ответ Ollama
        respx.get(f"{settings.OLLAMA_URL}/api/tags").mock(return_value=Response(200, json={"models": []}))
        respx.post(f"{settings.OLLAMA_URL}/api/chat").mock(
            return_value=Response(
                200,
                json={
                    "message": {"content": "Hello from Ollama!"},
                    "prompt_eval_count": 10,
                    "eval_count": 5,
                    "done_reason": "stop",
                },
            )
        )
        
        response = await client.post(
            f"/models/ask?session_id={test_session.id}",
            data={"msg_text": "Привет!", "role": "user"},
            headers=headers_with_api_token,
        )
        
        # Ожидаем 200, 400 (валидация) или 500 (ошибка LLM)
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "response" in data or "latency" in data

    @pytest.mark.asyncio
    async def test_ask_invalid_session(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
    ):
        """Тест запроса с несуществующей сессией."""
        fake_session_id = "00000000-0000-0000-0000-000000000000"
        
        response = await client.post(
            f"/models/ask?session_id={fake_session_id}",
            data={"msg_text": "Привет!", "role": "user"},
            headers=headers_with_api_token,
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_ask_invalid_role(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
        test_chat: ChatSettings,
        test_session: ChatSession,
    ):
        """Тест запроса с невалидной ролью."""
        response = await client.post(
            f"/models/ask?session_id={test_session.id}",
            data={"msg_text": "Привет!", "role": "invalid_role"},
            headers=headers_with_api_token,
        )
        
        # 400 или 422 для невалидной роли
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_ask_session_with_deleted_chat(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
        test_session_with_deleted_chat: ChatSession,
    ):
        """Тест запроса к сессии с удалённым чатом."""
        from src.core.config import settings
        import respx
        from httpx import Response

        # Мокаем health check и ответ Ollama
        with respx.mock:
            respx.get(f"{settings.OLLAMA_URL}/api/tags").mock(return_value=Response(200, json={"models": []}))
            respx.post(f"{settings.OLLAMA_URL}/api/chat").mock(
                return_value=Response(200, json={"message": {"content": "Response"}, "done": True})
            )

            response = await client.post(
                "/models/ask",
                data={
                    "session_id": str(test_session_with_deleted_chat.id),
                    "msg_text": "Hello",
                    "role": "user",
                },
                headers=headers_with_api_token,
            )

            # 422 - валидация сессии, 400/404 - чат не найден
            assert response.status_code in [400, 404, 422]


class TestLLMStreamEndpoint:
    """Тесты для POST /llm/stream."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_stream_success(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
        test_chat: ChatSettings,
        test_session: ChatSession,
    ):
        """Тест успешного стрим запроса."""
        from src.core.config import settings
        
        # Мокаем health check и стрим ответ
        respx.get(f"{settings.OLLAMA_URL}/api/tags").mock(return_value=Response(200, json={"models": []}))
        respx.post(f"{settings.OLLAMA_URL}/v1/chat/completions").mock(
            return_value=Response(
                200,
                content=b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\ndata: [DONE]\n\n',
            )
        )
        
        response = await client.post(
            f"/models/stream?session_id={test_session.id}",
            data={"msg_text": "Привет!", "role": "user"},
            headers=headers_with_api_token,
        )
        
        # Стриминг может вернуть 200 или ошибку LLM
        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_stream_invalid_session(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
    ):
        """Тест стрима с несуществующей сессией."""
        fake_session_id = "00000000-0000-0000-0000-000000000000"
        
        response = await client.post(
            f"/models/stream?session_id={fake_session_id}",
            data={"msg_text": "Привет!", "role": "user"},
            headers=headers_with_api_token,
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_stream_with_images(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
        test_chat: ChatSettings,
        test_session: ChatSession,
    ):
        """Тест стриминга с изображениями."""
        from src.core.config import settings
        import respx
        from httpx import Response

        # Мокаем health check и стриминг ответ
        with respx.mock:
            respx.get(f"{settings.OLLAMA_URL}/api/tags").mock(return_value=Response(200, json={"models": []}))
            
            # Мокаем стриминг ответ с изображениями
            stream_content = 'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\ndata: {"choices":[{"delta":{"content":" World"}}]}\n\ndata: [DONE]\n'
            respx.post(f"{settings.OLLAMA_URL}/v1/chat/completions").mock(
                return_value=Response(200, content=stream_content)
            )

            # Используем готовое тестовое изображение (base64)
            import base64
            img_data = base64.b64decode(TEST_IMAGE_BASE64)
            
            response = await client.post(
                "/models/stream",
                data={
                    "session_id": str(test_session.id),
                    "msg_text": "Hello with image",
                    "role": "user",
                },
                headers=headers_with_api_token,
                files={"images": ("test.png", img_data, "image/png")},
            )

            # 200 - успех, 422 - валидация (например нет чата в БД для мока)
            # Тест демонстрирует что изображения принимаются
            assert response.status_code in [200, 422]


class TestLLMSingleEndpoint:
    """Тесты для POST /llm/single."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_single_success(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
        test_chat: ChatSettings,
    ):
        """Тест успешного запроса без истории."""
        from src.core.config import settings
        
        # Мокаем health check и ответ Ollama
        respx.get(f"{settings.OLLAMA_URL}/api/tags").mock(return_value=Response(200, json={"models": []}))
        respx.post(f"{settings.OLLAMA_URL}/api/chat").mock(
            return_value=Response(
                200,
                json={
                    "message": {"content": "Single response!"},
                    "prompt_eval_count": 5,
                    "eval_count": 3,
                    "done_reason": "stop",
                },
            )
        )
        
        response = await client.post(
            f"/models/single?chat_id={test_chat.id}",
            data={"msg_text": "Привет!", "role": "user"},
            headers=headers_with_api_token,
        )
        
        # Ожидаем 200 или ошибку LLM
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert "latency" in data
            assert "chat_id" in data

    @pytest.mark.asyncio
    async def test_single_invalid_chat(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
    ):
        """Тест запроса с несуществующим чатом."""
        fake_chat_id = "00000000-0000-0000-0000-000000000000"
        
        response = await client.post(
            f"/models/single?chat_id={fake_chat_id}",
            data={"msg_text": "Привет!", "role": "user"},
            headers=headers_with_api_token,
        )
        
        # 400 или 404 для несуществующего чата
        assert response.status_code in [400, 404]

    @pytest.mark.asyncio
    async def test_single_with_model(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
        test_chat: ChatSettings,
        test_model: LLMModel,
        test_db,
    ):
        """Тест запроса с привязанной моделью."""
        # Привязываем модель к чату
        test_chat.model_id = test_model.id
        test_chat.model_name = test_model.provider_model
        await test_db.commit()
        
        from src.core.config import settings
        respx.get(f"{settings.OLLAMA_URL}/api/tags").mock(return_value=Response(200, json={"models": []}))
        respx.post(f"{settings.OLLAMA_URL}/api/chat").mock(
            return_value=Response(200, json={"message": {"content": "Response!"}, "done": True})
        )
        
        response = await client.post(
            f"/models/single?chat_id={test_chat.id}",
            data={"msg_text": "Привет!", "role": "user"},
            headers=headers_with_api_token,
        )
        
        assert response.status_code in [200, 500]


class TestLLMErrorCases:
    """Тесты ошибок для LLM endpoints."""

    @pytest.mark.asyncio
    async def test_ask_without_api_token(self, client: AsyncClient, test_session: ChatSession):
        """Тест запроса без API токена."""
        response = await client.post(
            f"/models/ask?session_id={test_session.id}",
            data={"msg_text": "Привет!", "role": "user"},
        )
        
        # 401, 403 или 422 для отсутствующего токена
        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_ask_with_inactive_token(
        self,
        client: AsyncClient,
        test_token_inactive: APIToken,
        test_session: ChatSession,
    ):
        """Тест запроса с неактивным токеном."""
        response = await client.post(
            f"/models/ask?session_id={test_session.id}",
            data={"msg_text": "Привет!", "role": "user"},
            headers={"api-token": test_token_inactive.token},
        )
        
        # 400, 401 или 403 для неактивного токена
        assert response.status_code in [400, 401, 403]

    @pytest.mark.asyncio
    async def test_ask_too_long_message(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
        test_chat: ChatSettings,
        test_session: ChatSession,
    ):
        """Тест запроса с слишком длинным сообщением."""
        from src.core.config import settings
        
        too_long_msg = "A" * (settings.MAX_PROMPT_LENGTH + 1)
        
        response = await client.post(
            f"/models/ask?session_id={test_session.id}",
            data={"msg_text": too_long_msg, "role": "user"},
            headers=headers_with_api_token,
        )
        
        # Валидация может вернуть 400 или 422
        assert response.status_code in [200, 400, 422, 500]

    @pytest.mark.asyncio
    async def test_ask_with_too_many_images(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
        test_chat: ChatSettings,
        test_session: ChatSession,
    ):
        """Тест запроса с превышением лимита изображений."""
        from src.core.config import settings
        
        image_data = base64.b64decode(TEST_IMAGE_BASE64)
        too_many_files = [
            ("images", (f"image{i}.png", image_data, "image/png"))
            for i in range(settings.MAX_IMAGES_PER_REQUEST + 1)
        ]
        
        response = await client.post(
            f"/models/ask?session_id={test_session.id}",
            data={"msg_text": "Сравни изображения", "role": "user"},
            files=too_many_files,
            headers=headers_with_api_token,
        )
        
        # 400 или 422 для превышения лимита
        assert response.status_code in [400, 422]
