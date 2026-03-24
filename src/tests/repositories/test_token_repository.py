"""
Тесты для TokenRepository.
"""

import pytest
from datetime import datetime, timezone

from src.database.api_token import APIToken
from src.domain.token.models import Token
from src.infrastructure.database.sqlalchemy_token_repository import SqlAlchemyTokenRepository


@pytest.mark.asyncio
class TestSqlAlchemyTokenRepository:
    """Тесты для SqlAlchemyTokenRepository."""

    async def test_create_token(self, test_db):
        """Создание токена."""
        repo = SqlAlchemyTokenRepository(test_db)
        
        token = Token(
            token_value="test_token_123",
            active=True,
            expires_at=None
        )
        
        created = await repo.create(token)
        
        assert created.token_id is not None
        assert created.token_value == "test_token_123"
        assert created.active is True

    async def test_get_by_id(self, test_db, test_token):
        """Получение токена по ID."""
        repo = SqlAlchemyTokenRepository(test_db)
        
        found = await repo.get_by_id(test_token.id)
        
        assert found is not None
        assert found.token_id == test_token.id
        assert found.token_value == test_token.token

    async def test_get_by_id_not_found(self, test_db):
        """Получение несуществующего токена."""
        repo = SqlAlchemyTokenRepository(test_db)
        
        found = await repo.get_by_id(99999)
        
        assert found is None

    async def test_get_by_token_value(self, test_db, test_token):
        """Получение токена по значению."""
        repo = SqlAlchemyTokenRepository(test_db)
        
        found = await repo.get_by_token_value(test_token.token)
        
        assert found is not None
        assert found.token_value == test_token.token

    async def test_get_by_token_value_not_found(self, test_db):
        """Получение несуществующего токена."""
        repo = SqlAlchemyTokenRepository(test_db)
        
        found = await repo.get_by_token_value("nonexistent")
        
        assert found is None

    async def test_get_inactive_token(self, test_db, test_token_inactive):
        """Получение неактивного токена (должен вернуть None)."""
        repo = SqlAlchemyTokenRepository(test_db)
        
        found = await repo.get_by_token_value(test_token_inactive.token)
        
        assert found is None

    async def test_update_token(self, test_db, test_token):
        """Обновление токена."""
        repo = SqlAlchemyTokenRepository(test_db)
        
        token = await repo.get_by_id(test_token.id)
        token.active = False
        
        updated = await repo.update(token)
        
        assert updated is not None
        assert updated.active is False

    async def test_delete_token(self, test_db, test_token):
        """Удаление токена."""
        repo = SqlAlchemyTokenRepository(test_db)
        
        await repo.delete(test_token.id)
        
        found = await repo.get_by_id(test_token.id)
        assert found is None

    async def test_list_tokens(self, test_db, test_token):
        """Получение списка токенов."""
        repo = SqlAlchemyTokenRepository(test_db)
        
        tokens = await repo.list(limit=10, offset=0)
        
        assert len(tokens) >= 1
        assert any(t.token_id == test_token.id for t in tokens)
