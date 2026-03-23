"""
Базовый интерфейс для LLM провайдеров.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator

from src.domain.llm.message import LLMMessage


class LLMProvider(ABC):
    """Абстрактный базовый класс для всех LLM провайдеров."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Название провайдера."""
        pass

    @abstractmethod
    async def chat_completion(
        self,
        model: str,
        messages: list[LLMMessage],
        temperature: float,
        max_tokens: int,
        context_window: int,
    ) -> str:
        """
        Запрос к LLM без стриминга.

        :param model: Название модели
        :param messages: Список сообщений
        :param temperature: Температура генерации
        :param max_tokens: Максимум токенов
        :param context_window: Размер контекста
        :return: Текст ответа
        """
        pass

    @abstractmethod
    async def stream_chat_completion(
        self,
        model: str,
        messages: list[LLMMessage],
        temperature: float,
        max_tokens: int,
        context_window: int,
    ) -> AsyncGenerator[str, None]:
        """
        Стриминг ответа от LLM.

        :param model: Название модели
        :param messages: Список сообщений
        :param temperature: Температура генерации
        :param max_tokens: Максимум токенов
        :param context_window: Размер контекста
        :yield: Чанки текста ответа
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Проверка доступности провайдера.

        :return: True если провайдер доступен
        """
        pass

    @abstractmethod
    async def get_available_models(self) -> list[str]:
        """
        Получение списка доступных моделей.

        :return: Список названий моделей
        """
        pass
