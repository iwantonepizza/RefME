"""
Интерфейс для подсчёта токенов.

Domain layer не знает о конкретных реализациях (tiktoken, etc).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class TokenCounter(ABC):
    """
    Интерфейс для подсчёта токенов.

    Используется в use cases для получения точного количества токенов.
    """

    @abstractmethod
    def count_prompt_tokens(self, messages: List[Dict[str, Any]], model: str) -> int:
        """
        Подсчёт количества токенов в промпте.

        :param messages: Список сообщений
        :param model: Название модели
        :return: Количество токенов
        """
        pass

    @abstractmethod
    def count_completion_tokens(self, text: str, model: str) -> int:
        """
        Подсчёт количества токенов в ответе.

        :param text: Текст ответа
        :param model: Название модели
        :return: Количество токенов
        """
        pass

    @abstractmethod
    def count_total_tokens(
        self,
        messages: List[Dict[str, Any]],
        completion_text: str,
        model: str,
    ) -> Dict[str, int]:
        """
        Подсчёт общего количества токенов.

        :param messages: Список сообщений
        :param completion_text: Текст ответа
        :param model: Название модели
        :return: Словарь с количеством токенов (prompt, completion, total)
        """
        pass
