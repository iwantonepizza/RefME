"""
Утилиты для получения эффективных настроек чата.

Приоритет настроек:
1. Настройки чата (если заданы)
2. Настройки модели из справочника
3. Дефолтные значения
"""

from src.database.chat import ChatSettings
from src.database.llm_model import LLMModel

DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096
DEFAULT_CONTEXT_WINDOW = 4096


def get_effective_settings(chat: ChatSettings) -> dict[str, float | int | str | None]:
    """
    Получение эффективных настроек для чата.

    Приоритет:
    1. Настройки чата (если не None)
    2. Настройки модели (если не None)
    3. Дефолтные значения

    :param chat: Объект чата
    :return: Словарь с эффективными настройками
    """
    model = chat.model if hasattr(chat, "model") and chat.model else None

    # Температура
    temperature = (
        chat.temperature
        if chat.temperature is not None
        else (model.temperature if model and model.temperature is not None else DEFAULT_TEMPERATURE)
    )

    # Max tokens
    max_tokens = (
        chat.max_tokens
        if chat.max_tokens is not None
        else (model.max_tokens if model and model.max_tokens is not None else DEFAULT_MAX_TOKENS)
    )

    # Context window
    context_window = (
        chat.context_window
        if chat.context_window is not None
        else (model.context_window if model and model.context_window is not None else DEFAULT_CONTEXT_WINDOW)
    )

    # Model name для запроса к LLM
    model_name = chat.model_name if chat.model_name else (model.provider_model if model else None)

    return {"model": model_name, "temperature": temperature, "max_tokens": max_tokens, "context_window": context_window}
