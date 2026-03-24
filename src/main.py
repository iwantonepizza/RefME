from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from src.core.config import settings
from src.exceptions import register_exception_handlers
from src.core.logging import logger
from src.core.metrics_middleware import MetricsMiddleware
from src.core.rate_limiter import limiter, rate_limit_exception_handler
from src.routers.v1.main_router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("LLM Gateway starting...")
    logger.info("Database migrations applied on container start")
    yield
    logger.info("LLM Gateway stopped")


app = FastAPI(
    title="LLM Gateway",
    lifespan=lifespan,
    version="1.0.2",
    docs_url="/models/docs",
    redoc_url="/models/redoc",
    openapi_url="/models/openapi.json",
)

# Регистрируем обработчики исключений
register_exception_handlers(app)

# Rate limiting (отключаем для тестов через app.state.limiter = None)
app.state.limiter = limiter
app.add_exception_handler(429, rate_limit_exception_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS.split(",") if settings.CORS_ALLOW_METHODS != "*" else ["*"],
    allow_headers=settings.CORS_ALLOW_HEADERS.split(",") if settings.CORS_ALLOW_HEADERS != "*" else ["*"],
)

app.add_middleware(MetricsMiddleware)

# Регистрируем роутеры
app.include_router(api_router, prefix="")

# Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
