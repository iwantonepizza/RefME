"""
Декоратор для логирования вызова методов.

Автоматически логирует:
- Вызов метода с именем и модулем
- Время выполнения
- Ошибки с traceback
"""

import functools
import logging
import time
from typing import Callable, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

# Типы для аннотаций
P = ParamSpec("P")  # Параметры функции
R = TypeVar("R")  # Возвращаемое значение


def logging_decorator(func: Callable[P, R]) -> Callable[P, R]:
    """
    Декоратор для логирования вызова методов.

    Логирует:
    - Полное имя метода (module.qualname)
    - Время начала выполнения
    - Время завершения с длительностью
    - Ошибки с временем выполнения

    Support: async функции
    """
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        func_name = f"{func.__module__}.{func.__qualname__}"
        start_time = time.perf_counter()

        logger.info(f"Метод {func_name} вызван")

        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            elapsed_time = time.perf_counter() - start_time
            logger.error(
                f"Метод {func_name} завершился ошибкой за {elapsed_time:.3f}s: {e}",
                exc_info=True
            )
            raise
        finally:
            elapsed_time = time.perf_counter() - start_time
            logger.info(f"Метод {func_name} завершен за {elapsed_time:.3f}s")

    return wrapper
