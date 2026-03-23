from typing import Any, Dict, List, Optional
"""
Use Case для запроса к LLM без истории сообщений.
"""

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import UploadFile

from src.core.constants import MessageStatus, Role
from src.core.logging import logger
from src.domain.chat.repositories import ChatRepository
from src.domain.llm.services import LLMConfigurationService
from src.domain.llm_model.repositories import ModelRepositoryInterface
from src.domain.token.models import Token
from src.domain.token.repositories import TokenRepository
from src.domain.utils.token_counter import TokenCounter
from src.exceptions.domain_exceptions import (
    ChatNotFoundError,
    InvalidInputError,
    TokenNotFoundError,
    TooManyImagesError,
)
from src.infrastructure.llm.providers.factory import get_provider_factory
from src.infrastructure.utils.effective_settings import get_effective_settings
from src.infrastructure.utils.image_helpers import encode_images_to_base64
from src.use_cases.base_use_case import BaseUseCase
from src.use_cases.llm.dto import EffectiveSettings, LLMSingleInput, LLMSingleOutput


@dataclass
class LLMSingleUseCaseInput:
    """Входные данные для запроса к LLM без истории."""
    api_token: Token
    chat_id: UUID
    msg_text: str | None = None
    role: str = "user"
    images: List[UploadFile | None] = None


class LLMSingleUseCase(BaseUseCase[LLMSingleUseCaseInput, LLMSingleOutput]):
    """Use Case для запроса к LLM без истории сообщений."""

    def __init__(
        self,
        token_repository: TokenRepository,
        chat_repository: ChatRepository,
        model_repository: ModelRepositoryInterface,
        config_service: LLMConfigurationService,
        token_counter: TokenCounter,  # ✅ Token Counter
    ):
        self.token_repository = token_repository
        self.chat_repository = chat_repository
        self.model_repository = model_repository
        self.config_service = config_service
        self.token_counter = token_counter
        self.llm_factory = get_provider_factory()

    async def _run_logic(self, input_data: LLMSingleUseCaseInput) -> LLMSingleOutput:
        """Выполнение запроса к LLM без истории."""
        # Получаем чат
        # Сначала получаем token ID из token value
        token_model = await self.token_repository.get_by_token_value(input_data.api_token.token_value)
        if not token_model:
            raise TokenNotFoundError()

        chat = await self.chat_repository.get_by_token_id_and_chat_id(
            token_model.token_id,
            input_data.chat_id
        )

        if not chat:
            raise ChatNotFoundError(chat_id=input_data.chat_id)

        # Проверяем роль
        request_role = input_data.role.strip().lower()
        if request_role not in (Role.USER.value, Role.SYSTEM.value):
            raise InvalidInputError(f"Invalid role '{request_role}'. Allowed: system, user")

        # Получаем эффективные настройки
        effective_settings = self._get_effective_settings(chat)

        # Обработка изображений
        images_data: List[str | None] = None
        if input_data.images:
            max_images = await self.config_service.get_max_images_per_request()
            if len(input_data.images) > max_images:
                raise TooManyImagesError(max_images)

            images_data = encode_images_to_base64(input_data.images)
            if not images_data:
                images_data = None

        # Формируем сообщения с поддержкой изображений
        if images_data:
            content_parts = [{"type": "text", "text": input_data.msg_text}] if input_data.msg_text else []
            for img in images_data:
                content_parts.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
            messages_payload = [{"role": request_role, "content": content_parts}]
        else:
            messages_payload = [{"role": request_role, "content": input_data.msg_text or ""}]

        start_time = time.time()

        # Выполняем запрос к LLM
        provider = await self.llm_factory.get_provider_for_model(
            effective_settings.model,
            self.model_repository
        )

        response_text = await provider.chat_completion({
            "model": effective_settings.model,
            "messages": messages_payload,
            "temperature": effective_settings.temperature,
            "max_tokens": effective_settings.max_tokens,
            "context_window": effective_settings.context_window,
        })

        # Обновляем last_used_at у токена
        await self._update_token_last_used(input_data.api_token.id)

        latency = time.time() - start_time

        return LLMSingleOutput(
            response=response_text,
            latency=latency,
            chat_id=input_data.chat_id,
        )

    def _get_effective_settings(self, chat) -> EffectiveSettings:
        """Получение эффективных настроек чата."""
        DEFAULT_MODEL = "llama2"  # Модель по умолчанию
        DEFAULT_TEMPERATURE = 0.7
        DEFAULT_MAX_TOKENS = 4096
        DEFAULT_CONTEXT_WINDOW = 4096

        # Используем model_name из чата или модель по умолчанию
        model_name = chat.model_name if chat.model_name else DEFAULT_MODEL

        temperature = (
            chat.temperature
            if chat.temperature is not None
            else DEFAULT_TEMPERATURE
        )

        max_tokens = (
            chat.max_tokens
            if chat.max_tokens is not None
            else DEFAULT_MAX_TOKENS
        )

        context_window = (
            chat.context_window
            if chat.context_window is not None
            else DEFAULT_CONTEXT_WINDOW
        )

        return EffectiveSettings(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            context_window=context_window,
        )

    async def _update_token_last_used(self, token_id: int) -> None:
        """Обновление last_used_at у токена."""
        token = await self.token_repository.get_by_id(token_id)
        if token:
            token.last_used_at = datetime.now(timezone.utc)
            await self.token_repository.update(token)
