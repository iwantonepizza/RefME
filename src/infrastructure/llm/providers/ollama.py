"""
Ollama провайдер для LLM.
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
    LLM_LATENCY,
    LLM_REQUESTS,
    LLM_TOKENS_IN,
    LLM_TOKENS_OUT,
)
from src.infrastructure.llm.providers.base import LLMProvider
from src.infrastructure.utils.retry import retry_async


class OllamaProvider(LLMProvider):
    """Провайдер для Ollama API."""

    def __init__(self, base_url: str, max_retries: int = 3, base_delay: float = 1.0):
        self.base_url = base_url
        self.max_retries = max_retries
        self.base_delay = base_delay

    @property
    def name(self) -> str:
        return "ollama"

    async def _make_chat_request(
        self,
        model: str,
        messages: list[LLMMessage],
        temperature: float,
        max_tokens: int,
        context_window: int,
    ) -> dict:
        """
        Выполнение запроса к Ollama API.

        :param model: Название модели
        :param messages: Список сообщений
        :param temperature: Температура генерации
        :param max_tokens: Максимум токенов
        :param context_window: Размер контекста
        :return: JSON ответ
        """
        logger.info("Отправка запроса к Ollama (API /api/chat)")

        request_data = {
            "model": model,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": temperature,
            "num_predict": max_tokens,
            "num_ctx": context_window,
            "stream": False,
        }

        logger.debug(f"Ollama request: {request_data}")

        async with httpx.AsyncClient(timeout=240) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=request_data)
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
        Запрос к LLM через нативный Ollama API: POST /api/chat (stream=false)

        Поддерживает мультимодальные запросы с изображениями.
        Формат Ollama: {model, messages: [{role, content, images}], stream, options}

        :param model: Название модели
        :param messages: Список сообщений
        :param temperature: Температура генерации
        :param max_tokens: Максимум токенов
        :param context_window: Размер контекста
        :return: Текст ответа
        """
        logger.info("Формирование запроса к Ollama")

        start = time.perf_counter()

        LLM_REQUESTS.labels(model=model, type="chat").inc()

        # Выполняем запрос через _make_chat_request
        response = await self._make_chat_request(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            context_window=context_window,
        )

        # Получаем текст ответа
        response_text = response.get("message", {}).get("content", "")

        # Обновляем метрики
        usage = response.get("prompt_eval_count", 0)
        completion_tokens = response.get("eval_count", 0)

        LLM_TOKENS_IN.labels(model=model).inc(usage)
        LLM_TOKENS_OUT.labels(model=model).inc(completion_tokens)

        elapsed = time.perf_counter() - start
        LLM_LATENCY.labels(model=model, type="chat").observe(elapsed)

        cpu = psutil.cpu_percent()
        ram = f"{psutil.virtual_memory().used} / {psutil.virtual_memory().total}"
        logger.info("Ответ от Ollama получен")

        logger.info(
            "Данные запроса | model: %s | latency: %.3fs | prompt_tokens: %s | completion_tokens: %s | "
            "finish_reason: %s | cpu: %s | ram: %s",
            model,
            elapsed,
            usage,
            completion_tokens,
            response.get("done_reason"),
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
        Стриминг ответа от Ollama.

        Возвращает текстовые чанки контента (delta.content).
        На завершение отдаёт "[DONE]\n".

        :param model: Название модели
        :param messages: Список сообщений
        :param temperature: Температура генерации
        :param max_tokens: Максимум токенов
        :param context_window: Размер контекста
        :yield: Чанки текста ответа
        """
        start = time.perf_counter()

        LLM_REQUESTS.labels(model=model, type="stream").inc()

        tokens = 0

        try:
            # Таймаут 5 минут для стриминга
            async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0)) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/v1/chat/completions",
                    json={
                        "model": model,
                        "messages": [msg.to_dict() for msg in messages],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": True,
                    },
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

                        delta = obj.get("choices", [{}])[0].get("delta", {}).get("content")
                        if not delta:
                            continue

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
        """Проверка доступности Ollama."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            logger.error(f"Ollama health check failed: {self.base_url}")
            return False

    async def get_available_models(self) -> list[str]:
        """Получение списка доступных моделей Ollama."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()

                data = resp.json()
                models = [m["name"] for m in data.get("models", [])]
                return models
        except Exception as e:
            logger.error(f"Failed to get Ollama models: {e}")
            return []

    async def get_model_info(self, model_name: str) -> dict:
        """Получение информации о модели через /api/show."""
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{self.base_url}/api/show",
                json={"name": model_name},
            )
            resp.raise_for_status()
            return resp.json()
