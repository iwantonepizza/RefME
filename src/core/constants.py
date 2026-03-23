"""
Константы и Enum для приложения.
"""

from enum import StrEnum


class MessageStatus(StrEnum):
    """Статусы обработки сообщений."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ModelType(StrEnum):
    """Типы моделей."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


class Role(StrEnum):
    """Роли сообщений."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ProviderType(StrEnum):
    """Типы LLM провайдеров."""

    OLLAMA = "ollama"
    VLLM = "vllm"


# Жёсткие ограничения (не из .env)
MAX_CONTEXT_WINDOW = 128000  # максимальный размер контекста
MAX_PROMPT_LENGTH = 32000  # максимальная длина промпта
MAX_MESSAGE_LENGTH = 32000  # максимальная длина сообщения
