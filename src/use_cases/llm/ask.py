from typing import Any, Dict, List
"""
Use Case для запроса к LLM с историей сообщений.
"""

import time
from dataclasses import dataclass
from typing import List
from uuid import UUID

from fastapi import UploadFile

from src.core.constants import MessageStatus, Role
from src.core.logging import logger
from src.domain.chat.repositories import ChatRepository
from src.domain.llm.orchestrator import LLMOrchestrator
from src.domain.llm_model.repositories import ModelRepository
from src.domain.message.models import Message
from src.domain.message.repositories import MessageRepository
from src.domain.session.repositories import SessionRepository
from src.domain.token.models import Token
from src.domain.token.repositories import TokenRepository
from src.domain.utils.token_counter import TokenCounter
from src.exceptions.domain_exceptions import (
    ChatNotFoundError,
    InvalidInputError,
    SessionNotBoundToChatError,
    SessionNotFoundError,
    TokenNotFoundError,
)
from src.infrastructure.utils.effective_settings import get_effective_settings
from src.use_cases.base_use_case import BaseUseCase
from src.use_cases.llm.dto import EffectiveSettings, LLMRequestInput, LLMRequestOutput
from src.domain.llm.message import LLMMessage

# Флаг доступности метрик
METRICS_AVAILABLE = True


@dataclass
class LLMAskInput:
    """Входные данные для запроса к LLM."""
    api_token: Token
    session_id: UUID
    msg_text: str | None = None
    role: str = "user"
    images: List[UploadFile | None] = None


@dataclass
class LLMAskOutput:
    """Результат запроса к LLM."""
    response: str
    latency: float
    session_id: UUID


class LLMAskUseCase(BaseUseCase[LLMAskInput, LLMAskOutput]):
    """Use Case для запроса к LLM с историей сообщений."""

    def __init__(
        self,
        token_repository: TokenRepository,
        session_repository: SessionRepository,
        chat_repository: ChatRepository,
        message_repository: MessageRepository,
        model_repository: ModelRepository,
        orchestrator: LLMOrchestrator,
        token_counter: TokenCounter,
    ):
        self.token_repository = token_repository
        self.session_repository = session_repository
        self.chat_repository = chat_repository
        self.message_repository = message_repository
        self.model_repository = model_repository
        self.orchestrator = orchestrator
        self.token_counter = token_counter

    async def _run_logic(self, input_data: LLMAskInput) -> LLMAskOutput:
        """Выполнение запроса к LLM."""
        # Получаем сессию
        session = await self.session_repository.get_by_token_id_and_session_id(
            input_data.api_token.token_value,
            input_data.session_id
        )

        if not session:
            raise SessionNotFoundError(session_id=input_data.session_id)

        if not session.chat_id:
            raise SessionNotBoundToChatError(session_id=input_data.session_id)

        # Проверяем роль
        request_role = input_data.role.strip().lower()
        if request_role not in (Role.USER.value, Role.SYSTEM.value):
            raise InvalidInputError(f"Invalid role '{request_role}'. Allowed: system, user")

        # System сообщение сохраняем, но ответ не запрашиваем
        if request_role == Role.SYSTEM.value:
            await self.message_repository.create(Message(
                session_id=session.session_id,
                role=Role.SYSTEM.value,
                content=input_data.msg_text,
                status=MessageStatus.COMPLETED.value
            ))
            return LLMAskOutput(
                response="System message saved",
                latency=0,
                session_id=session.session_id,
            )

        # Получаем чат
        # Сначала получаем token ID из token value
        token_model = await self.token_repository.get_by_token_value(input_data.api_token.token_value)
        if not token_model:
            raise TokenNotFoundError()

        chat = await self.chat_repository.get_by_token_id_and_chat_id(
            token_model.token_id,
            session.chat_id
        )

        if not chat:
            raise ChatNotFoundError(chat_id=session.chat_id)

        # Получаем эффективные настройки
        effective_settings = self._get_effective_settings(chat)

        logger.info(
            f"Эффективные настройки: model={effective_settings.model}, "
            f"temperature={effective_settings.temperature}, "
            f"max_tokens={effective_settings.max_tokens}, "
            f"context_window={effective_settings.context_window}"
        )

        # Обработка изображений через сервис
        images_data: List[str] | None = None
        if input_data.images:
            from src.infrastructure.services.image_service import ImageService
            images_data = await ImageService.process_images(input_data.images)

        # Формируем messages payload
        messages_payload = await self._build_messages_payload(
            session.session_id,
            request_role,
            input_data.msg_text,
            images_data
        )

        start_time = time.time()

        # Сохраняем сообщение пользователя
        user_msg = input_data.msg_text or ""
        if user_msg:
            await self.message_repository.create(Message(
                session_id=session.session_id,
                role=request_role,
                content=user_msg,
                status=MessageStatus.COMPLETED.value,
            ))

        # Выполняем запрос к LLM через orchestrator
        # Сначала выбираем провайдера для модели
        from src.infrastructure.llm.providers.factory import get_provider_factory
        llm_factory = get_provider_factory()
        provider = await llm_factory.get_provider_for_model(
            effective_settings.model,
            self.model_repository
        )
        
        response_text = await self.orchestrator.generate(
            provider=provider,
            model=effective_settings.model,
            messages=messages_payload,
            temperature=effective_settings.temperature,
            max_tokens=effective_settings.max_tokens,
            context_window=effective_settings.context_window,
        )

        latency = time.time() - start_time

        # Сохраняем ответ ассистента
        if response_text:
            await self.message_repository.create(Message(
                session_id=session.session_id,
                role=Role.ASSISTANT.value,
                content=response_text,
                status=MessageStatus.COMPLETED.value,
            ))

        # Записываем метрики через сервис
        if METRICS_AVAILABLE:
            from src.infrastructure.services.llm_metrics_service import LLMMetricsService
            metrics_service = LLMMetricsService(self.token_counter)
            messages_dict = [msg.to_dict() for msg in messages_payload]
            metrics_service.record_request(
                model=effective_settings.model,
                latency=latency,
                messages=messages_dict,
                response_text=response_text,
            )

        return LLMAskOutput(
            response=response_text,
            latency=latency,
            session_id=session.session_id,
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

    async def _build_messages_payload(
        self,
        session_id: UUID,
        role: str,
        msg_text: str | None,
        images_data: List[str | None] = None
    ) -> List[LLMMessage]:
        """Построение payload для LLM запроса."""
        # Получаем историю сообщений
        messages = await self.message_repository.get_by_session_id(session_id, limit=None, offset=0)

        # Формируем историю
        history = [LLMMessage(role=Role(msg.role), content=msg.content) for msg in messages]

        # Формируем новое сообщение
        new_message = LLMMessage(
            role=Role(role),
            content=msg_text or "",
            images=images_data,
        )

        history.append(new_message)
        return history
