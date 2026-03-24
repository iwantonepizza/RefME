"""
Тесты для TokenConverter сервиса.
"""

import pytest
from datetime import datetime, timezone

from src.database.api_token import APIToken
from src.domain.token.models import Token as DomainToken
from src.infrastructure.services.token_converter import TokenConverter


class TestTokenConverter:
    """Тесты для TokenConverter."""

    def test_convert_orm_to_domain(self):
        """Конвертация ORM модели в domain."""
        orm_token = APIToken(
            id=1,
            token="test_token_value",
            active=True,
            created_at=datetime.now(timezone.utc),
            expires_at=None,
            last_used_at=None,
            deleted_at=None
        )
        
        domain_token = TokenConverter.to_domain(orm_token)
        
        assert isinstance(domain_token, DomainToken)
        assert domain_token.token_id == 1
        assert domain_token.token_value == "test_token_value"
        assert domain_token.active is True

    def test_convert_domain_returns_same(self):
        """Domain модель возвращается как есть."""
        domain_token = DomainToken(
            token_id=1,
            token_value="test_token",
            active=True
        )
        
        result = TokenConverter.to_domain(domain_token)
        
        assert result is domain_token
        assert isinstance(result, DomainToken)

    def test_convert_with_all_fields(self):
        """Конвертация со всеми полями."""
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=30)  # expires_at в будущем
        
        orm_token = APIToken(
            id=42,
            token="full_token",
            active=False,
            created_at=now,
            expires_at=future,  # В будущем
            last_used_at=now,
            deleted_at=None
        )
        
        domain_token = TokenConverter.to_domain(orm_token)
        
        assert domain_token.token_id == 42
        assert domain_token.token_value == "full_token"
        assert domain_token.active is False
        assert domain_token.created_at == now
        assert domain_token.expires_at == future
        assert domain_token.last_used_at == now
        assert domain_token.deleted_at is None
