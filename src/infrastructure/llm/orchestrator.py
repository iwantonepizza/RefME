"""
Реализация LLM Orchestrator.

Orchestrator инкапсулирует логику вызова LLM провайдеров.
Провайдер выбирается ВНЕ orchestrator (в use case) и передаётся готовым.
"""

import logging
from typing import AsyncGenerator, List

from src.domain.llm.message import LLMMessage
from src.domain.llm.orchestrator import LLMOrchestrator
from src.infrastructure.llm.providers.base import LLMProvider

logger = logging.getLogger(__name__)


class LLMOrchestratorImpl(LLMOrchestrator):
    """Реализация LLM Orchestrator."""

    def __init__(self):
        """
        Инициализация orchestrator.
        
        Провайдеры передаются через методы generate/stream.
        """
        pass

    async def generate(
        self,
        provider: LLMProvider,
        model: str,
        messages: List[LLMMessage],
        temperature: float,
        max_tokens: int,
        context_window: int,
    ) -> str:
        """
        Генерация ответа от LLM (без стриминга).
        
        :param provider: Готовый провайдер (выбран в use case)
        :param model: Название модели
        :param messages: Список сообщений
        :param temperature: Температура генерации
        :param max_tokens: Максимум токенов
        :param context_window: Размер контекста
        :return: Текст ответа
        """
        logger.info(f"LLM запрос: provider={provider.name}, model={model}")

        # Выполняем запрос через провайдер
        response = await provider.chat_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            context_window=context_window,
        )

        logger.info(f"LLM ответ получен: {len(response)} символов")
        return response

    async def stream(
        self,
        provider: LLMProvider,
        model: str,
        messages: List[LLMMessage],
        temperature: float,
        max_tokens: int,
        context_window: int,
    ) -> AsyncGenerator[str, None]:
        """
        Стриминг ответа от LLM.
        
        :param provider: Готовый провайдер (выбран в use case)
        :param model: Название модели
        :param messages: Список сообщений
        :param temperature: Температура генерации
        :param max_tokens: Максимум токенов
        :param context_window: Размер контекста
        :yield: Чанки текста ответа
        """
        logger.info(f"LLM стрим: provider={provider.name}, model={model}")

        # Стримим ответ через провайдер
        async for chunk in provider.stream_chat_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            context_window=context_window,
        ):
            yield chunk

        logger.info("LLM стрим завершён")
