"""
Реализация подсчёта токенов через tiktoken.

Использует библиотеку tiktoken для точного подсчёта токенов.
"""

import logging
from typing import Any, Dict, List

from src.domain.utils.token_counter import TokenCounter

logger = logging.getLogger(__name__)


class TiktokenTokenCounter(TokenCounter):
    """
    Реализация TokenCounter через tiktoken.

    Использует encoding для конкретной модели или fallback на cl100k_base.
    """

    def count_prompt_tokens(self, messages: List[Dict[str, Any]], model: str) -> int:
        """
        Подсчёт количества токенов в промпте.

        :param messages: Список сообщений
        :param model: Название модели
        :return: Количество токенов
        """
        encoding = self._get_encoding(model)

        total = 0
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total += len(encoding.encode(content))
            # Добавляем токены за структуру сообщений
            total += 4

        return total

    def count_completion_tokens(self, text: str, model: str) -> int:
        """
        Подсчёт количества токенов в ответе.

        :param text: Текст ответа
        :param model: Название модели
        :return: Количество токенов
        """
        encoding = self._get_encoding(model)
        return len(encoding.encode(text))

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
        prompt_tokens = self.count_prompt_tokens(messages, model)
        completion_tokens = self.count_completion_tokens(completion_text, model)

        return {
            "prompt": prompt_tokens,
            "completion": completion_tokens,
            "total": prompt_tokens + completion_tokens,
        }

    def _get_encoding(self, model: str) -> object:
        """
        Получение encoding для модели.

        :param model: Название модели
        :return: Encoding объект
        """
        try:
            import tiktoken
            # Пытаемся получить encoding для конкретной модели
            return tiktoken.encoding_for_model(model)
        except (KeyError, ImportError):
            # Fallback на cl100k_base (используется для GPT-4, GPT-3.5-Turbo)
            try:
                import tiktoken
                return tiktoken.get_encoding("cl100k_base")
            except ImportError:
                logger.warning("tiktoken not installed, using fallback estimation")
                return _FallbackEncoding()


class _FallbackEncoding:
    """
    Fallback encoding когда tiktoken недоступен.

    Использует простую эвристику: 1 токен ≈ 4 символа.
    """

    def encode(self, text: str) -> List[int]:
        """Эмуляция encode через длину текста."""
        # Возвращаем список "токенов" для совместимости
        return list(range(len(text) // 4))

    def __len__(self) -> int:
        return 0


# Глобальный экземпляр
_counter: TokenCounter | None = None


def get_token_counter() -> TokenCounter:
    """Получение глобального экземпляра счётчика токенов."""
    global _counter
    if _counter is None:
        _counter = TiktokenTokenCounter()
    return _counter


def reset_token_counter() -> None:
    """Сброс счётчика (для тестов)."""
    global _counter
    _counter = None
