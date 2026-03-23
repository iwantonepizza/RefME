"""
Обработчики domain событий.

Используются для:
- Audit logging (аудит действий)
- Метрики (Prometheus)
- Уведомления
"""

import logging
from src.domain.events.base import DomainEvent
from src.domain.events.chat_events import ChatCreated, ChatUpdated, ChatDeleted
from src.domain.events.token_events import TokenCreated, TokenUpdated, TokenDeleted
from src.domain.events.session_events import SessionCreated, SessionDeleted

logger = logging.getLogger(__name__)


# ==================== Audit Logging ====================


async def log_chat_created(event: ChatCreated) -> None:
    """Аудит: чат создан."""
    logger.info(
        f"AUDIT: Chat created - ID={event.chat_id}, Token ID={event.token_id}, Name={event.name}",
        extra={
            "audit_event": "chat_created",
            "chat_id": str(event.chat_id),
            "token_id": event.token_id,
        }
    )


async def log_chat_updated(event: ChatUpdated) -> None:
    """Аудит: чат обновлён."""
    logger.info(
        f"AUDIT: Chat updated - ID={event.chat_id}, Fields={event.updated_fields}",
        extra={
            "audit_event": "chat_updated",
            "chat_id": str(event.chat_id),
            "updated_fields": event.updated_fields,
        }
    )


async def log_chat_deleted(event: ChatDeleted) -> None:
    """Аудит: чат удалён."""
    logger.info(
        f"AUDIT: Chat deleted - ID={event.chat_id}, Token ID={event.token_id}",
        extra={
            "audit_event": "chat_deleted",
            "chat_id": str(event.chat_id),
            "token_id": event.token_id,
        }
    )


async def log_token_created(event: TokenCreated) -> None:
    """Аудит: токен создан."""
    logger.info(
        f"AUDIT: Token created - ID={event.token_id}, Expires={event.expires_at}",
        extra={
            "audit_event": "token_created",
            "token_id": event.token_id,
        }
    )


async def log_token_deleted(event: TokenDeleted) -> None:
    """Аудит: токен удалён."""
    logger.info(
        f"AUDIT: Token deleted - ID={event.token_id}",
        extra={
            "audit_event": "token_deleted",
            "token_id": event.token_id,
        }
    )


async def log_session_created(event: SessionCreated) -> None:
    """Аудит: сессия создана."""
    logger.info(
        f"AUDIT: Session created - ID={event.session_id}, Chat ID={event.chat_id}",
        extra={
            "audit_event": "session_created",
            "session_id": str(event.session_id),
            "chat_id": str(event.chat_id),
        }
    )


async def log_session_deleted(event: SessionDeleted) -> None:
    """Аудит: сессия удалена."""
    logger.info(
        f"AUDIT: Session deleted - ID={event.session_id}",
        extra={
            "audit_event": "session_deleted",
            "session_id": str(event.session_id),
        }
    )


# ==================== Обработчики для регистрации ====================


def register_event_handlers(event_bus) -> None:
    """Регистрация всех обработчиков событий."""
    # Chat events
    event_bus.subscribe(ChatCreated, log_chat_created)
    event_bus.subscribe(ChatUpdated, log_chat_updated)
    event_bus.subscribe(ChatDeleted, log_chat_deleted)
    
    # Token events
    event_bus.subscribe(TokenCreated, log_token_created)
    event_bus.subscribe(TokenDeleted, log_token_deleted)
    
    # Session events
    event_bus.subscribe(SessionCreated, log_session_created)
    event_bus.subscribe(SessionDeleted, log_session_deleted)
    
    logger.info("Event handlers registered")
