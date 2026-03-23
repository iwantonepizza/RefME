"""
vLLM провайдер для LLM.

vLLM использует OpenAI-compatible API:
POST /v1/chat/completions
GET /v1/models
GET /health
"""

import json
import time
from typing import AsyncGenerator

import httpx
import psutil

from src.core.config import settings
from src.core.logging import logger
from src.domain.llm.message import LLMMessage
from src.prometheus.metrics.llm import (
    LLM_ERRORS,
    LLM_FIRST_TOKEN_LATENCY,
    LLM_LATENCY,
    LLM_REQUESTS,
    LLM_TOKENS_IN,
    LLM_TOKENS_OUT,
)
from src.infrastructure.llm.providers.base import LLMProvider
from src.infrastructure.utils.retry import retry_async


class VLLMProvider(LLMProvider):
    """
    Провайдер для vLLM.

    vLLM использует стандартный OpenAI API формат:
    - POST /v1/chat/completions для запросов
    - GET /v1/models для списка моделей
    - GET /health для проверки здоровья
    """

    def __init__(self, base_url: str, api_key: str | None = None):
        self.base_url = base_url
        self.api_key = api_key
        self._models_cache: set[str] = set()

    @property
    def name(self) -> str:
        return "vllm"

    def _get_headers(self) -> dict[str, str]:
        """Получение заголовков для запросов."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def _make_chat_request(
        self,
        model: str,
        messages: list[LLMMessage],
        temperature: float,
        max_tokens: int,
        context_window: int,
        url: str,
    ) -> dict:
        """
        Выполнение запроса к vLLM API.

        :param model: Название модели
        :param messages: Список сообщений
        :param temperature: Температура генерации
        :param max_tokens: Максимум токенов
        :param context_window: Размер контекста
        :param url: URL endpoint
        :return: JSON ответ
        """
        request_data = {
            "model": model,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "max_completion_tokens": context_window,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                url,
                json=request_data,
                headers=self._get_headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def chat_completion(
        self,
        model: str,
        messages: list[LLMMessage],
        temperature: float,
        max_tokens: int,
        context_window: int,
    ) -> str:
        """
        Запрос к vLLM через OpenAI-compatible API.

        vLLM формат запроса:
        {
            "model": "meta-llama/Llama-2-7b-chat-hf",
            "messages": [{"role": "user", "content": "..."}],
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": false
        }

        :param model: Название модели
        :param messages: Список сообщений
        :param temperature: Температура генерации
        :param max_tokens: Максимум токенов
        :param context_window: Размер контекста
        :return: Текст ответа
        """
        logger.info("Формирование запроса к vLLM")

        start = time.perf_counter()

        LLM_REQUESTS.labels(model=model, type="chat").inc()

        # vLLM использует стандартный OpenAI формат
        response = await self._make_chat_request(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            context_window=context_window,
            url=f"{self.base_url}/v1/chat/completions",
        )

        # Получаем текст ответа
        response_text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        if response_text is None:
            raise RuntimeError(f"vLLM: missing content in response. Got: {response}")

        # Метрики токенов
        usage = response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        LLM_TOKENS_IN.labels(model=model).inc(prompt_tokens)
        LLM_TOKENS_OUT.labels(model=model).inc(completion_tokens)

        elapsed = time.perf_counter() - start
        LLM_LATENCY.labels(model=model, type="chat").observe(elapsed)

        cpu = psutil.cpu_percent()
        ram = f"{psutil.virtual_memory().used} / {psutil.virtual_memory().total}"
        logger.info("Ответ от vLLM получен")

        logger.info(
            "Данные запроса | model: %s | latency: %.3fs | prompt_tokens: %s | "
            "completion_tokens: %s | cpu: %s | ram: %s",
            model,
            elapsed,
            prompt_tokens,
            completion_tokens,
            cpu,
            ram,
        )
        return response_text

    async def stream_chat_completion(
        self,
        model: str,
        messages: list[LLMMessage],
        temperature: float,
        max_tokens: int,
        context_window: int,
    ) -> AsyncGenerator[str, None]:
        """
        Стриминг ответа от vLLM.

        Возвращает текстовые чанки в формате Server-Sent Events.
        На завершение отдаёт "[DONE]\n".

        :param model: Название модели
        :param messages: Список сообщений
        :param temperature: Температура генерации
        :param max_tokens: Максимум токенов
        :param context_window: Размер контекста
        :yield: Чанки текста ответа
        """
        start = time.perf_counter()
        first_token_time = None
        tokens = 0

        LLM_REQUESTS.labels(model=model, type="stream").inc()

        request_data = {
            "model": model,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            # Таймаут 5 минут для стриминга
            async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0)) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/v1/chat/completions",
                    json=request_data,
                    headers=self._get_headers(),
                ) as resp:
                    resp.raise_for_status()

                    async for line in resp.aiter_lines():
                        if not line:
                            continue

                        raw = line.strip()
                        data_str = raw

                        if raw.startswith("data:"):
                            data_str = raw[len("data:") :].strip()

                        if data_str == "[DONE]":
                            yield "[DONE]\n"
                            continue

                        try:
                            obj = json.loads(data_str)
                        except Exception:
                            continue

                        # OpenAI формат стриминга
                        delta = obj.get("choices", [{}])[0].get("delta", {}).get("content")
                        if not delta:
                            continue

                        if first_token_time is None:
                            first_token_time = time.perf_counter() - start
                            LLM_FIRST_TOKEN_LATENCY.labels(model=model).observe(first_token_time)

                        tokens += 1
                        yield delta

        except Exception:
            LLM_ERRORS.labels(model=model, type="stream").inc()
            raise

        finally:
            total = time.perf_counter() - start
            LLM_LATENCY.labels(model=model, type="stream").observe(total)
            LLM_TOKENS_OUT.labels(model=model).inc(tokens)

    async def health_check(self) -> bool:
        """Проверка доступности vLLM."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/health", headers=self._get_headers())
                return resp.status_code == 200
        except Exception:
            logger.error(f"vLLM health check failed: {self.base_url}")
            return False

    async def get_available_models(self) -> list[str]:
        """Получение списка доступных моделей vLLM."""
        if self._models_cache:
            return list(self._models_cache)

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/v1/models", headers=self._get_headers())
                resp.raise_for_status()

                data = resp.json()
                models = [m["id"] for m in data.get("data", [])]
                self._models_cache = set(models)
                return models
        except httpx.ConnectError as e:
            logger.error(f"vLLM server unavailable: {self.base_url}")
            raise
        except Exception as e:
            logger.error(f"Failed to get vLLM models: {e}")
            raise

    def clear_models_cache(self) -> None:
        """Очистка кэша моделей."""
        self._models_cache.clear()
        logger.info("vLLM models cache cleared")
