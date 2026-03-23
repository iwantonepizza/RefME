"""
Event Bus для публикации domain событий.

Поддерживает:
- Синхронные обработчики
- Асинхронные обработчики
- Подписку на конкретные типы событий
"""

import inspect
import logging
from abc import ABC, abstractmethod
from typing import Callable

from src.domain.events.base import DomainEvent

logger = logging.getLogger(__name__)


# Тип обработчика событий
EventHandler = Callable[[DomainEvent], None] | Callable[[DomainEvent], object]


class EventBus(ABC):
    """
    Интерфейс Event Bus.

    Используется для публикации domain событий.
    """

    @abstractmethod
    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """Подписка на событие."""
        pass

    @abstractmethod
    def unsubscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """Отписка от события."""
        pass

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Публикация события."""
        pass


class InMemoryEventBus(EventBus):
    """
    In-memory реализация Event Bus.

    Хранит подписки в памяти. Подходит для single-instance приложений.
    """

    def __init__(self):
        self._subscribers: dict[type[DomainEvent], list[EventHandler]] = {}

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """Подписка на событие."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"Handler {handler.__name__} subscribed to {event_type.__name__}")

    def unsubscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """Отписка от события."""
        if event_type in self._subscribers:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)
                logger.debug(f"Handler {handler.__name__} unsubscribed from {event_type.__name__}")

    async def publish(self, event: DomainEvent) -> None:
        """
        Публикация события всем подписчикам.

        Обработчики вызываются последовательно.
        Ошибки в одном обработчике не влияют на другие.
        """
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])

        if not handlers:
            logger.debug(f"No subscribers for {event_type.__name__}")
            return

        logger.debug(f"Publishing {event_type.__name__} to {len(handlers)} subscribers")

        for handler in handlers:
            try:
                # Проверяем, асинхронный ли обработчик
                if inspect.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in event handler {handler.__name__}: {e}", exc_info=True)


# Глобальный экземпляр
_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Получение глобального экземпляра Event Bus."""
    global _event_bus
    if _event_bus is None:
        _event_bus = InMemoryEventBus()
    return _event_bus


def reset_event_bus() -> None:
    """Сброс Event Bus (для тестов)."""
    global _event_bus
    _event_bus = None
