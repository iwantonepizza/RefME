"""
Реализация LLM Orchestrator.

Orchestrator инкапсулирует логику работы с LLM providers:
- Выбор провайдера для модели
- Вызов provider (chat/stream)
- Обработку ответов
"""

import logging
from typing import AsyncGenerator, List

from src.domain.llm.message import LLMMessage
from src.domain.llm.orchestrator import LLMOrchestrator
from src.domain.llm_model.repositories import ModelRepositoryInterface
from src.infrastructure.llm.providers.factory import LLMProviderFactory

logger = logging.getLogger(__name__)


class LLMOrchestratorImpl(LLMOrchestrator):
    """Реализация LLM Orchestrator."""

    def __init__(
        self,
        model_repository: ModelRepositoryInterface,
        llm_factory: LLMProviderFactory,
    ):
        self.model_repository = model_repository
        self.llm_factory = llm_factory

    async def generate(
        self,
        model: str,
        messages: List[LLMMessage],
        temperature: float,
        max_tokens: int,
        context_window: int,
    ) -> str:
        """
        Генерация ответа от LLM (без стриминга).
        """
        logger.info(f"LLM запрос: model={model}, messages_count={len(messages)}")

        # Получаем провайдер для модели через factory
        provider = await self.llm_factory.get_provider_for_model(
            model,
            self.model_repository
        )

        # Выполняем запрос
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
        model: str,
        messages: List[LLMMessage],
        temperature: float,
        max_tokens: int,
        context_window: int,
    ) -> AsyncGenerator[str, None]:
        """
        Стриминг ответа от LLM.
        """
        logger.info(f"LLM стрим: model={model}, messages_count={len(messages)}")

        # Получаем провайдер для модели через factory
        provider = await self.llm_factory.get_provider_for_model(
            model,
            self.model_repository
        )

        # Стримим ответ
        async for chunk in provider.stream_chat_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            context_window=context_window,
        ):
            yield chunk

        logger.info("LLM стрим завершён")
