import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.prometheus.metrics.http import (
    HTTP_IN_PROGRESS,
    HTTP_LATENCY,
    HTTP_REQUESTS,
)

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        HTTP_IN_PROGRESS.inc()
        start = time.perf_counter()

        # Инициализируем статусом 500 по умолчанию
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response

        except Exception as e:
            logger.error(f"Middleware error: {e}", exc_info=True)
            # Не меняем status_code — останется 500 для необработанных исключений
            raise

        finally:
            elapsed = time.perf_counter() - start

            HTTP_REQUESTS.labels(method=method, path=path, status=str(status_code)).inc()

            HTTP_LATENCY.labels(path=path).observe(elapsed)
            HTTP_IN_PROGRESS.dec()
