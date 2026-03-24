"""
Сервис для записи метрик LLM запросов.

Инкапсулирует логику записи метрик Prometheus.
"""

import logging
from typing import List

from src.domain.utils.token_counter import TokenCounter

logger = logging.getLogger(__name__)


class LLMMetricsService:
    """Сервис для записи метрик LLM."""

    def __init__(self, token_counter: TokenCounter):
        self.token_counter = token_counter

    def record_request(
        self,
        model: str,
        latency: float,
        messages: List[dict],
        response_text: str,
        status: str = "success"
    ) -> None:
        """
        Запись метрик LLM запроса.

        :param model: Название модели
        :param latency: Время выполнения (секунды)
        :param messages: Список сообщений (dict)
        :param response_text: Текст ответа
        :param status: Статус запроса
        """
        # Импорты метрик
        try:
            from src.prometheus.metrics.llm import (
                LLM_LATENCY,
                LLM_REQUESTS,
                LLM_TOKENS_IN,
                LLM_TOKENS_OUT,
            )
        except ImportError:
            logger.warning("Prometheus metrics not available")
            return

        # Запись метрик
        LLM_REQUESTS.labels(model=model, type="chat").inc()
        LLM_LATENCY.labels(model=model, type="chat").observe(latency)

        # Подсчёт токенов
        prompt_tokens = self.token_counter.count_prompt_tokens(messages, model)
        completion_tokens = self.token_counter.count_completion_tokens(response_text, model)

        LLM_TOKENS_IN.labels(model=model).inc(prompt_tokens)
        LLM_TOKENS_OUT.labels(model=model).inc(completion_tokens)

        logger.debug(
            f"LLM metrics recorded: model={model}, latency={latency:.3f}s, "
            f"prompt_tokens={prompt_tokens}, completion_tokens={completion_tokens}"
        )
