"""Интерфейс для LLM Orchestrator."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, List

from src.domain.llm.message import LLMMessage
from src.infrastructure.llm.providers.base import LLMProvider


class LLMOrchestrator(ABC):
    """Интерфейс для LLM Orchestrator."""

    @abstractmethod
    async def generate(
        self,
        provider: LLMProvider,
        model: str,
        messages: List[LLMMessage],
        temperature: float,
        max_tokens: int,
        context_window: int,
    ) -> str:
        """Генерация ответа от LLM (без стриминга).

        :param provider: LLM провайдер (выбран в use case)
        :param model: Название модели
        :param messages: Список сообщений
        :param temperature: Температура генерации (0.0-2.0)
        :param max_tokens: Максимум токенов для генерации
        :param context_window: Размер контекстного окна
        :return: Текст ответа
        """
        pass

    @abstractmethod
    async def stream(
        self,
        provider: LLMProvider,
        model: str,
        messages: List[LLMMessage],
        temperature: float,
        max_tokens: int,
        context_window: int,
    ) -> AsyncGenerator[str, None]:
        """Стриминг ответа от LLM.

        :param provider: LLM провайдер (выбран в use case)
        :param model: Название модели
        :param messages: Список сообщений
        :param temperature: Температура генерации (0.0-2.0)
        :param max_tokens: Максимум токенов для генерации
        :param context_window: Размер контекстного окна
        :return: Асинхронный генератор текста
        """
        pass
