"""
Domain модель токена.
"""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Token:
    """Бизнес-объект токена."""
    token_id: int = 0
    token_value: str = ""
    active: bool = True
    created_at: datetime | None = None
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    deleted_at: datetime | None = None

    def __post_init__(self):
        """Валидация токена при создании."""
        # Проверяем что токен не пустой
        if not self.token_value:
            raise ValueError("token_value не может быть пустым")

        # Проверяем что expires_at в будущем (если установлен)
        if self.expires_at and self.expires_at < datetime.now(timezone.utc):
            raise ValueError("expires_at не может быть в прошлом")

    @property
    def is_expired(self) -> bool:
        """Проверка истечения срока действия."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_active(self) -> bool:
        """Проверка активности токена."""
        return self.active and not self.is_expired and self.deleted_at is None
