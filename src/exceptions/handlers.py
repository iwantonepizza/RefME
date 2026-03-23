"""
Обработчики исключений для FastAPI.

Регистрирует глобальные обработчики для:
- Domain исключений (400, 401, 403, 404, 409, 503)
- Приложений исключений
- HTTP исключений
- Валидации
- Необработанных исключений
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.exceptions.exceptions import AppException
from src.exceptions.domain_exceptions import (
    DomainException,
    NotFoundError,
    AlreadyExistsError,
    IncorrectValueError,
    TokenInvalidError,
    TokenInactiveError,
    TooManyImagesError,
    InvalidRoleError,
    LLMProviderError,
    NoAvailableProviderError,
)
from src.core.logging import logger


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрация обработчиков исключений."""

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
        """Базовый обработчик domain исключений."""
        logger.warning(
            f"Domain exception: {exc.error_code} - {exc.message}",
            extra={
                "method": request.method,
                "error_code": exc.error_code,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
            },
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        """Обработчик ошибок 'не найдено'."""
        logger.warning(
            f"Not found: {exc.entity_name} with {exc.field_name}={exc.field_value}",
            extra={
                "method": request.method,
                "error_code": exc.error_code,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
                "details": {
                    "entity_name": exc.entity_name,
                    "field_name": exc.field_name,
                    "field_value": str(exc.field_value) if exc.field_value else None,
                },
            },
        )

    @app.exception_handler(AlreadyExistsError)
    async def already_exists_handler(request: Request, exc: AlreadyExistsError) -> JSONResponse:
        """Обработчик ошибок 'уже существует'."""
        logger.warning(
            f"Already exists: {exc.entity_name} with {exc.field_name}={exc.field_value}",
            extra={
                "method": request.method,
                "error_code": exc.error_code,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
                "details": {
                    "entity_name": exc.entity_name,
                    "field_name": exc.field_name,
                    "field_value": str(exc.field_value),
                },
            },
        )

    @app.exception_handler(IncorrectValueError)
    async def incorrect_value_handler(request: Request, exc: IncorrectValueError) -> JSONResponse:
        """Обработчик ошибок 'неверное значение'."""
        logger.warning(
            f"Incorrect value: {exc.message}",
            extra={
                "method": request.method,
                "error_code": exc.error_code,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
            },
        )

    @app.exception_handler(TooManyImagesError)
    async def too_many_images_handler(request: Request, exc: TooManyImagesError) -> JSONResponse:
        """Обработчик ошибок 'слишком много изображений'."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
            },
        )

    @app.exception_handler(InvalidRoleError)
    async def invalid_role_handler(request: Request, exc: InvalidRoleError) -> JSONResponse:
        """Обработчик ошибок 'неверная роль'."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
            },
        )

    @app.exception_handler(TokenInvalidError)
    async def token_invalid_handler(request: Request, exc: TokenInvalidError) -> JSONResponse:
        """Обработчик ошибок 'невалидный токен'."""
        logger.warning(
            f"Token invalid: {exc.message}",
            extra={
                "method": request.method,
                "error_code": exc.error_code,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
            },
        )

    @app.exception_handler(TokenInactiveError)
    async def token_inactive_handler(request: Request, exc: TokenInactiveError) -> JSONResponse:
        """Обработчик ошибок 'токен не активен'."""
        logger.warning(
            f"Token inactive: {exc.message}",
            extra={
                "method": request.method,
                "error_code": exc.error_code,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
            },
        )

    @app.exception_handler(LLMProviderError)
    async def llm_provider_error_handler(request: Request, exc: LLMProviderError) -> JSONResponse:
        """Обработчик ошибок 'LLM провайдер недоступен'."""
        logger.error(
            f"LLM provider error: {exc.provider_name} - {exc.message}",
            extra={
                "method": request.method,
                "error_code": exc.error_code,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
            },
        )

    @app.exception_handler(NoAvailableProviderError)
    async def no_available_provider_handler(request: Request, exc: NoAvailableProviderError) -> JSONResponse:
        """Обработчик ошибок 'нет доступного провайдера'."""
        logger.error(
            f"No available provider: {exc.message}",
            extra={
                "method": request.method,
                "error_code": exc.error_code,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
            },
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Обработчик кастомных исключений приложения."""
        logger.warning(
            f"App exception: {exc.error_code} - {exc.message}",
            extra={
                "method": request.method,
                "error_code": exc.error_code,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Обработчик HTTP исключений."""
        # Не логируем 404 для статических файлов
        if exc.status_code != 404 or not request.url.path.startswith("/docs"):
            logger.warning(
                f"HTTP exception: {exc.status_code} - {exc.detail}",
                extra={
                    "method": request.method,
                },
            )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "http_error",
                "message": str(exc.detail),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Обработчик ошибок валидации запроса."""
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(x) for x in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        logger.warning(
            f"Validation error: {errors}",
            extra={
                "method": request.method,
            },
        )

        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Ошибка валидации запроса",
                "details": errors,
            },
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Обработчик ошибок валидации Pydantic."""
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(x) for x in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        logger.warning(
            f"Pydantic validation error: {errors}",
            extra={
                "method": request.method,
            },
        )

        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Ошибка валидации данных",
                "details": errors,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Обработчик всех необработанных исключений."""
        logger.error(
            f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
            exc_info=True,
            extra={
                "method": request.method,
            },
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "Внутренняя ошибка сервера",
            },
        )
