"""
Тесты для LLM провайдеров (Ollama, vLLM).
"""

import pytest
import respx
from httpx import Response

from src.infrastructure.llm.providers.factory import (
    LLMProviderFactory,
    get_provider_factory,
    reset_provider_factory,
)
from src.infrastructure.llm.providers.ollama import OllamaProvider
from src.infrastructure.llm.providers.vllm import VLLMProvider


class TestOllamaProvider:
    """Тесты для Ollama провайдера."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_chat_completion_success(self):
        """Тест успешного запроса к Ollama."""
        # Мок ответа Ollama
        respx.post("http://test:11434/api/chat").mock(
            return_value=Response(
                200,
                json={
                    "model": "llama2",
                    "message": {"role": "assistant", "content": "Hello!"},
                    "done": True,
                    "prompt_eval_count": 10,
                    "eval_count": 5,
                },
            )
        )

        provider = OllamaProvider("http://test:11434")
        result = await provider.chat_completion(
            {
                "model": "llama2",
                "messages": [{"role": "user", "content": "Hi"}],
                "temperature": 0.7,
                "max_tokens": 100,
            }
        )

        assert result == "Hello!"

    @pytest.mark.asyncio
    @respx.mock
    async def test_chat_completion_with_retry(self):
        """Тест запроса к Ollama с retry после timeout."""
        from httpx import TimeoutException
        
        # Первые два запроса - timeout, третий - успех
        respx.post("http://test:11434/api/chat").mock(
            side_effect=[
                TimeoutException("Timeout 1"),
                TimeoutException("Timeout 2"),
                Response(
                    200,
                    json={
                        "model": "llama2",
                        "message": {"role": "assistant", "content": "Hello after retry!"},
                        "done": True,
                    },
                ),
            ]
        )

        provider = OllamaProvider("http://test:11434", max_retries=3, base_delay=0.1)
        result = await provider.chat_completion(
            {
                "model": "llama2",
                "messages": [{"role": "user", "content": "Hi"}],
            }
        )

        assert result == "Hello after retry!"
        assert respx.calls.call_count == 3

    @pytest.mark.asyncio
    @respx.mock
    async def test_chat_completion_retry_exhausted(self):
        """Тест исчерпания retry попыток."""
        from httpx import TimeoutException
        
        # Все запросы - timeout
        respx.post("http://test:11434/api/chat").mock(
            side_effect=[TimeoutException(f"Timeout {i}") for i in range(4)]
        )

        provider = OllamaProvider("http://test:11434", max_retries=3, base_delay=0.05)
        
        with pytest.raises(Exception):
            await provider.chat_completion(
                {
                    "model": "llama2",
                    "messages": [{"role": "user", "content": "Hi"}],
                }
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_health_check_success(self):
        """Тест проверки здоровья Ollama."""
        respx.get("http://test:11434/api/tags").mock(return_value=Response(200, json={"models": []}))

        provider = OllamaProvider("http://test:11434")
        result = await provider.health_check()

        assert result is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_health_check_failure(self):
        """Тест проверки здоровья Ollama (недоступен)."""
        respx.get("http://test:11434/api/tags").mock(side_effect=Exception("Connection refused"))

        provider = OllamaProvider("http://test:11434")
        result = await provider.health_check()

        assert result is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_available_models(self):
        """Тест получения списка моделей."""
        respx.get("http://test:11434/api/tags").mock(
            return_value=Response(
                200,
                json={
                    "models": [
                        {"name": "llama2"},
                        {"name": "mistral"},
                    ]
                },
            )
        )

        provider = OllamaProvider("http://test:11434")
        models = await provider.get_available_models()

        assert len(models) == 2
        assert "llama2" in models
        assert "mistral" in models


class TestVLLMProvider:
    """Тесты для vLLM провайдера."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_chat_completion_success(self):
        """Тест успешного запроса к vLLM."""
        # Мок ответа vLLM (OpenAI format) - retry нужен 1 успешный вызов
        route = respx.post("http://test:8000/v1/chat/completions")
        route.mock(
            return_value=Response(
                200,
                json={
                    "id": "test",
                    "choices": [
                        {"message": {"role": "assistant", "content": "Hello from vLLM!"}, "finish_reason": "stop"}
                    ],
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                    },
                },
            )
        )

        provider = VLLMProvider("http://test:8000")
        result = await provider.chat_completion(
            {
                "model": "meta-llama/Llama-2-7b-chat-hf",
                "messages": [{"role": "user", "content": "Hi"}],
                "temperature": 0.7,
                "max_tokens": 100,
            }
        )

        assert result == "Hello from vLLM!"
        assert route.called

    @pytest.mark.asyncio
    @respx.mock
    async def test_chat_completion_with_context_window(self):
        """Тест запроса к vLLM с context_window."""
        route = respx.post("http://test:8000/v1/chat/completions")
        route.mock(
            return_value=Response(
                200,
                json={
                    "choices": [{"message": {"content": "Hello!"}}],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5},
                },
            )
        )

        provider = VLLMProvider("http://test:8000")
        result = await provider.chat_completion(
            {
                "model": "test",
                "messages": [{"role": "user", "content": "Hi"}],
                "context_window": 8192,
            }
        )

        assert result == "Hello!"
        assert route.called

    @pytest.mark.asyncio
    @respx.mock
    async def test_stream_chat_completion_success(self):
        """Тест успешного стриминга от vLLM."""
        stream_content = (
            'data: {"choices":[{"delta":{"content":"Hello"}}]}\n'
            'data: {"choices":[{"delta":{"content":" World"}}]}\n'
            'data: [DONE]\n'
        )
        respx.post("http://test:8000/v1/chat/completions").mock(
            return_value=Response(200, content=stream_content)
        )

        provider = VLLMProvider("http://test:8000")
        chunks = []
        async for chunk in provider.stream_chat_completion(
            {
                "model": "test",
                "messages": [{"role": "user", "content": "Hi"}],
            }
        ):
            chunks.append(chunk)

        assert len(chunks) == 3
        assert chunks[0] == "Hello"
        assert chunks[1] == " World"
        assert chunks[2] == "[DONE]\n"

    @pytest.mark.asyncio
    @respx.mock
    async def test_chat_completion_with_api_key(self):
        """Тест запроса к vLLM с API ключом."""
        route = respx.post("http://test:8000/v1/chat/completions")
        route.mock(return_value=Response(200, json={"choices": [{"message": {"content": "Hello!"}}]}))

        provider = VLLMProvider("http://test:8000", api_key="test-key")
        result = await provider.chat_completion(
            {
                "model": "test",
                "messages": [{"role": "user", "content": "Hi"}],
            }
        )

        # Проверяем что заголовок Authorization был отправлен
        assert result == "Hello!"
        assert route.called
        request = route.calls.last.request
        assert "Authorization" in request.headers
        assert request.headers["Authorization"] == "Bearer test-key"

    @pytest.mark.asyncio
    @respx.mock
    async def test_health_check_success(self):
        """Тест проверки здоровья vLLM."""
        respx.get("http://test:8000/health").mock(return_value=Response(200, text="OK"))

        provider = VLLMProvider("http://test:8000")
        result = await provider.health_check()

        assert result is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_health_check_failure(self):
        """Тест проверки здоровья vLLM (недоступен)."""
        respx.get("http://test:8000/health").mock(side_effect=Exception("Connection refused"))

        provider = VLLMProvider("http://test:8000")
        result = await provider.health_check()

        assert result is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_available_models(self):
        """Тест получения списка моделей vLLM."""
        respx.get("http://test:8000/v1/models").mock(
            return_value=Response(
                200,
                json={
                    "data": [
                        {"id": "meta-llama/Llama-2-7b-chat-hf"},
                        {"id": "mistralai/Mistral-7B-Instruct-v0.2"},
                    ]
                },
            )
        )

        provider = VLLMProvider("http://test:8000")
        models = await provider.get_available_models()

        assert len(models) == 2
        assert "meta-llama/Llama-2-7b-chat-hf" in models

    @pytest.mark.asyncio
    async def test_models_cache(self):
        """Тест кеширования списка моделей."""
        # Создаём провайдер без мока - используем кеш
        provider = VLLMProvider("http://test:8000")

        # Добавляем модели в кеш вручную
        provider._models_cache = {"model1", "model2"}

        # Должно вернуть из кеша без запроса
        models = await provider.get_available_models()

        assert len(models) == 2
        assert "model1" in models
        assert "model2" in models

    def test_clear_models_cache(self):
        """Тест очистки кеша моделей."""
        provider = VLLMProvider("http://test:8000")
        provider._models_cache = {"model1", "model2"}
        
        provider.clear_models_cache()
        
        assert len(provider._models_cache) == 0


class TestLLMProviderFactory:
    """Тесты для фабрики провайдеров."""

    def setup_method(self):
        """Сброс фабрики перед каждым тестом."""
        reset_provider_factory()

    def test_factory_initialization(self):
        """Тест инициализации фабрики."""
        factory = get_provider_factory()

        providers = factory.get_all_providers()

        assert "ollama" in providers

    def test_register_provider(self):
        """Тест регистрации провайдера."""
        factory = LLMProviderFactory()

        # Создаём тестовый провайдер
        class TestProvider:
            name = "test"

        factory.register("test", TestProvider())

        assert "test" in factory.get_all_providers()

    def test_unregister_provider(self):
        """Тест удаления провайдера."""
        factory = LLMProviderFactory()
        factory.register("temp", type("TempProvider", (), {"name": "temp"})())

        assert "temp" in factory.get_all_providers()

        factory.unregister("temp")

        assert "temp" not in factory.get_all_providers()

    def test_get_provider(self):
        """Тест получения провайдера."""
        factory = LLMProviderFactory()

        provider = factory.get_provider("ollama")

        assert provider is not None
        assert provider.name == "ollama"

    def test_get_nonexistent_provider(self):
        """Тест получения несуществующего провайдера."""
        factory = LLMProviderFactory()

        provider = factory.get_provider("nonexistent")

        assert provider is None


class TestRetryUtils:
    """Тесты для утилит retry."""

    @pytest.mark.asyncio
    async def test_retry_async_success_first_try(self):
        """Тест успешного выполнения с первой попытки."""
        from src.infrastructure.utils.retry import retry_async

        async def success_func():
            return "success"

        result = await retry_async(success_func, max_retries=3)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_async_success_after_retries(self):
        """Тест успешного выполнения после нескольких попыток."""
        from src.infrastructure.utils.retry import retry_async

        attempt_count = 0

        async def flaky_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError(f"Attempt {attempt_count} failed")
            return "success"

        result = await retry_async(flaky_func, max_retries=3, base_delay=0.01)
        assert result == "success"
        assert attempt_count == 3

    @pytest.mark.asyncio
    async def test_retry_async_exhausted(self):
        """Тест исчерпания всех попыток."""
        from src.infrastructure.utils.retry import RetryError, retry_async

        async def always_fail():
            raise ValueError("Always fails")

        with pytest.raises(RetryError):
            await retry_async(always_fail, max_retries=2, base_delay=0.01)

    @pytest.mark.asyncio
    async def test_retry_async_with_specific_exceptions(self):
        """Тест retry только для определённых исключений."""
        from src.infrastructure.utils.retry import retry_async

        attempt_count = 0

        async def flaky_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ConnectionError(f"Attempt {attempt_count} failed")
            return "success"

        # Retry только для ConnectionError
        result = await retry_async(
            flaky_func,
            max_retries=3,
            base_delay=0.01,
            exceptions=(ConnectionError,),
        )
        assert result == "success"

    def test_retry_decorator(self):
        """Тест декоратора retry."""
        from src.infrastructure.utils.retry import retry_decorator

        call_count = 0

        @retry_decorator(max_retries=2, base_delay=0.01)
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Fail")
            return "success"

        import asyncio
        result = asyncio.run(flaky_func())
        assert result == "success"
        assert call_count == 2
