"""
Утилиты для retry логики.
"""

import asyncio
import random
from functools import wraps
from typing import Callable, Type, TypeVar

from src.core.logging import logger

T = TypeVar("T")


class RetryError(Exception):
    """Исключение при исчерпании попыток retry."""

    def __init__(self, message: str, last_exception: Exception | None = None):
        self.message = message
        self.last_exception = last_exception
        super().__init__(self.message)


async def retry_async(
    func: Callable[..., T],
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple[Type[Exception], ...] | None = None,
    **kwargs,
) -> T:
    """
    Асинхронная функция для выполнения с retry логикой.

    :param func: Асинхронная функция для выполнения
    :param args: Позиционные аргументы для функции
    :param max_retries: Максимальное количество попыток
    :param base_delay: Базовая задержка между попытками (секунды)
    :param max_delay: Максимальная задержка (секунды)
    :param exponential_base: База экспоненциальной задержки
    :param jitter: Добавлять ли случайную составляющую к задержке
    :param exceptions: Кортеж исключений для retry (None = все исключения)
    :param kwargs: Именованные аргументы для функции
    :return: Результат выполнения функции
    :raises RetryError: Если все попытки исчерпаны
    """
    if exceptions is None:
        exceptions = (Exception,)

    last_exception = None

    for attempt in range(max_retries + 1):  # +1 для первой попытки без задержки
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        except exceptions as e:  # type: ignore
            last_exception = e

            if attempt >= max_retries:
                logger.error(f"Все попытки исчерпаны после {max_retries} retry")
                raise RetryError(f"Все попытки исчерпаны после {max_retries} retry", last_exception) from e

            # Рассчитываем задержку
            delay = min(base_delay * (exponential_base**attempt), max_delay)

            if jitter:
                # Добавляем случайную составляющую до 25% от delay
                delay = delay * (0.75 + random.random() * 0.5)

            logger.warning(
                f"Попытка {attempt + 1}/{max_retries} не удалась: {type(e).__name__}: {e}. "
                f"Следующая попытка через {delay:.2f}s"
            )

            await asyncio.sleep(delay)

    # Должно быть unreachable, но на всякий случай
    raise RetryError(f"Все попытки исчерпаны после {max_retries} retry", last_exception)


def retry_decorator(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple[type[Exception], ...] | None = None,
):
    """
    Декоратор для retry логики.

    :param max_retries: Максимальное количество попыток
    :param base_delay: Базовая задержка между попытками (секунды)
    :param max_delay: Максимальная задержка (секунды)
    :param exponential_base: База экспоненциальной задержки
    :param jitter: Добавлять ли случайную составляющую к задержке
    :param exceptions: Кортеж исключений для retry
    :return: Декоратор
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_async(
                func,
                *args,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter,
                exceptions=exceptions,
                **kwargs,
            )

        return wrapper

    return decorator
