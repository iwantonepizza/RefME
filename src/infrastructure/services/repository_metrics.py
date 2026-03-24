"""
Метрики для репозиториев.

Отслеживает:
- Количество запросов к репозиториям
- Время выполнения операций
- Ошибки репозиториев
"""

import time
from functools import wraps
from typing import Any, Callable, TypeVar

from src.prometheus.metrics.http import REPOSITORY_LATENCY, REPOSITORY_REQUESTS

T = TypeVar('T')


def repository_metrics_decorator(
    repository_name: str,
    operation: str
):
    """
    Декоратор для записи метрик репозиториев.

    :param repository_name: Название репозитория (например, "chat_repository")
    :param operation: Название операции (например, "get_by_id", "create")
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.perf_counter()
            status = "success"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                elapsed = time.perf_counter() - start
                REPOSITORY_REQUESTS.labels(
                    repository=repository_name,
                    operation=operation,
                    status=status
                ).inc()
                REPOSITORY_LATENCY.labels(
                    repository=repository_name,
                    operation=operation
                ).observe(elapsed)

        return wrapper
    return decorator
