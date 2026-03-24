"""
Настройки приложения.
Все значения загружаются из environment variables.
"""

from typing import List

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Обязательные
    DATABASE_URL: str
    AUTH_SERVICE_URL: str
    OLLAMA_URL: str

    # vLLM настройки (опционально)
    VLLM_URL: str | None = None
    VLLM_API_KEY: str | None = None

    # Приоритет провайдеров (порядок использования)
    # Формат в .env: LLM_PROVIDER_PRIORITY_RAW=vllm,ollama (строка через запятую)
    # Используем _RAW + property для обратной совместимости — .env проще редактировать как строку
    # Pydantic v2 не парсит JSON из env по умолчанию для list[str]
    LLM_PROVIDER_PRIORITY_RAW: str = "vllm,ollama"
    
    @property
    def LLM_PROVIDER_PRIORITY(self) -> list[str]:
        """
        Получение списка приоритетов провайдеров.
        
        :return: Список провайдеров ['vllm', 'ollama']
        
        Примечание: Значение парсится из строки в .env файле.
        Это компромисс между явностью типа и удобством редактирования .env.
        """
        return [p.strip() for p in self.LLM_PROVIDER_PRIORITY_RAW.split(",")]

    APP_NAME: str = "LLM-gate"
    DEBUG: bool = False

    # CORS настройки
    CORS_ORIGINS: str = "*"  # Можно указать несколько через запятую
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"

    # Rate limiting настройки (запросов в минуту)
    LLM_RATE_LIMIT: int = 60  # LLM эндпоинты (/ask, /stream, /single)
    ADMIN_RATE_LIMIT: int = 30  # Админские эндпоинты
    DEFAULT_RATE_LIMIT: int = 100  # Остальные эндпоинты (токены, чаты, сессии)

    # Ограничения на размер данных
    MAX_PROMPT_LENGTH: int = 32000  # Максимальная длина промпта в СИМВОЛАХ (не токенах!)
    MAX_IMAGE_SIZE_MB: int = 10  # Максимальный размер изображения в мегабайтах
    MAX_IMAGES_PER_REQUEST: int = 5  # Максимальное количество изображений в одном запросе

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Проверка формата DATABASE_URL."""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL должен быть PostgreSQL URL (postgresql:// или postgresql+asyncpg://)")
        return v

    @field_validator("AUTH_SERVICE_URL", "OLLAMA_URL", "VLLM_URL")
    @classmethod
    def validate_urls(cls, v: str | None) -> str | None:
        """Проверка что URL начинается с http:// или https://."""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("URL должен начинаться с http:// или https://")
        return v

    @field_validator("LLM_RATE_LIMIT", "ADMIN_RATE_LIMIT", "DEFAULT_RATE_LIMIT")
    @classmethod
    def validate_rate_limits(cls, v: int) -> int:
        """Проверка что rate limits положительные."""
        if v <= 0:
            raise ValueError("Rate limit должен быть положительным числом")
        return v

    @field_validator("MAX_PROMPT_LENGTH", "MAX_IMAGE_SIZE_MB", "MAX_IMAGES_PER_REQUEST")
    @classmethod
    def validate_limits(cls, v: int) -> int:
        """Проверка что лимиты положительные."""
        if v <= 0:
            raise ValueError("Лимит должен быть положительным числом")
        return v

    def get_cors_origins_list(self) -> List[str]:
        """Получение списка CORS origins."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
