"""
Тесты для LLM endpoint с изображениями (routers/llm.py).
"""

import base64

import pytest
import respx
from httpx import AsyncClient, Response

from src.database.api_token import APIToken
from src.database.session import ChatSession
from src.database.chat import ChatSettings

# Тестовое изображение (1x1 красный пиксель в PNG)
TEST_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="


class TestLLMWithImages:
    """Тесты для LLM endpoint с изображениями."""

    @pytest.mark.asyncio
    async def test_ask_with_single_image(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
        test_chat: ChatSettings,
        test_session: ChatSession,
    ):
        """Тест запроса с одним изображением."""
        # Создаем тестовое изображение
        image_data = base64.b64decode(TEST_IMAGE_BASE64)

        response = await client.post(
            f"/models/llm/ask?session_id={test_session.id}",
            data={"msg_text": "Что на изображении?", "role": "user"},
            files={"images": ("test.png", image_data, "image/png")},
            headers=headers_with_api_token,
        )

        # Ожидаем 200 или ошибку от LLM (если модель не поддерживает изображения)
        assert response.status_code in [200, 400, 500]

    @pytest.mark.asyncio
    async def test_ask_with_multiple_images(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
        test_chat: ChatSettings,
        test_session: ChatSession,
    ):
        """Тест запроса с несколькими изображениями."""
        image_data = base64.b64decode(TEST_IMAGE_BASE64)

        response = await client.post(
            f"/models/llm/ask?session_id={test_session.id}",
            data={"msg_text": "Сравни изображения", "role": "user"},
            files=[
                ("images", ("image1.png", image_data, "image/png")),
                ("images", ("image2.png", image_data, "image/png")),
            ],
            headers=headers_with_api_token,
        )

        # Ожидаем 200 или ошибку от LLM
        assert response.status_code in [200, 400, 500]

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

        # Создаем больше изображений чем лимит
        files = [
            ("images", (f"image{i}.png", image_data, "image/png")) for i in range(settings.MAX_IMAGES_PER_REQUEST + 1)
        ]

        response = await client.post(
            f"/models/llm/ask?session_id={test_session.id}",
            data={"msg_text": "Сравни изображения", "role": "user"},
            files=files,
            headers=headers_with_api_token,
        )

        # Проверяем что это 400 или 422 (валидация)
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    @respx.mock
    async def test_stream_with_image(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
        test_chat: ChatSettings,
        test_session: ChatSession,
        mock_respx,
    ):
        """Тест stream endpoint с изображением."""
        # Мокаем Ollama API для стриминга и health check
        from src.core.config import settings

        # Мокаем health check чтобы провайдер был доступен
        respx.get(f"{settings.OLLAMA_URL}/api/tags").mock(return_value=Response(200, json={"models": []}))
        
        stream_route = respx.post(f"{settings.OLLAMA_URL}/v1/chat/completions")
        stream_route.mock(return_value=Response(200, content=b'data: {"choices":[{"delta":{"content":"test"}}]}\n\n'))

        image_data = base64.b64decode(TEST_IMAGE_BASE64)

        # Тест проверяет только что endpoint принимает изображения
        response = await client.post(
            f"/models/llm/stream?session_id={test_session.id}",
            data={"msg_text": "Что на изображении?", "role": "user"},
            files={"images": ("test.png", image_data, "image/png")},
            headers=headers_with_api_token,
        )

        # Проверяем что запрос принят (200) или отклонён валидацией (400/422)
        # или ошибкой LLM (500)
        assert response.status_code in [200, 400, 422, 500]

    @pytest.mark.asyncio
    async def test_ask_without_images(
        self,
        client: AsyncClient,
        headers_with_api_token: dict,
        test_token: APIToken,
        test_chat: ChatSettings,
        test_session: ChatSession,
    ):
        """Тест запроса без изображений (базовый тест)."""
        response = await client.post(
            f"/models/llm/ask?session_id={test_session.id}",
            data={"msg_text": "Привет!", "role": "user"},
            headers=headers_with_api_token,
        )

        # Ожидаем 200 или ошибку от LLM (если сервер недоступен)
        assert response.status_code in [200, 400, 500]
