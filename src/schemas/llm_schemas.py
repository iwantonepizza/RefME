from typing import List
"""
Схемы для LLM запросов.
"""

from typing import Union

from pydantic import BaseModel, Field, field_validator


class ImageContent(BaseModel):
    """Изображение в формате base64 или URL."""

    type: str = Field(default="image_url", description="Тип контента")
    image_url: dict[str, str] | None = Field(
        default=None,
        description="URL изображения или base64 (ключ 'url')",
    )
    source: dict[str, object] | None = Field(
        default=None,
        description="Альтернативный источник изображения (для Ollama format)",
    )


class RequestModelSchema(BaseModel):
    """Схема запроса к LLM."""

    msg: str | None = Field(default=None, description="Текстовое сообщение")
    role: str | None = Field(default="user", description="Роль: user, system")
    images: list[str | dict[str, object]] | None = Field(
        default=None,
        description="Список изображений (base64 строки или dict с параметрами)",
    )

    @field_validator("images", mode="before")
    @classmethod
    def validate_images(cls, v):
        """Преобразует пустую строку или пустой список в None."""
        if v is None:
            return None
        if isinstance(v, str) and v.strip() == "":
            return None
        if isinstance(v, list) and len(v) == 0:
            return None
        return v
