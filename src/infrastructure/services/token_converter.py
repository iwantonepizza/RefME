"""
Сервис для конвертации токенов.

Устраняет дублирование кода конвертации ORM → Domain моделей.
"""

from src.database.api_token import APIToken
from src.domain.token.models import Token as DomainToken


class TokenConverter:
    """Сервис для конвертации между ORM и Domain моделями токенов."""

    @staticmethod
    def to_domain(api_token: APIToken | DomainToken) -> DomainToken:
        """
        Конвертация ORM/API токена в Domain модель.

        :param api_token: ORM модель APIToken или уже Domain модель
        :return: Domain модель Token
        """
        # Если уже domain модель — возвращаем как есть
        if isinstance(api_token, DomainToken):
            return api_token

        # Конвертируем ORM модель в domain
        return DomainToken(
            token_id=api_token.id,
            token_value=api_token.token_value if hasattr(api_token, 'token_value') else api_token.token,
            active=api_token.active,
            created_at=api_token.created_at,
            expires_at=api_token.expires_at,
            last_used_at=api_token.last_used_at,
            deleted_at=api_token.deleted_at if hasattr(api_token, 'deleted_at') else None,
        )
