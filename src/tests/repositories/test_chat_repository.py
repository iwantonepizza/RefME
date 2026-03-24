"""
Тесты для ChatRepository.
"""

import pytest
from uuid import UUID

from src.database.chat import ChatSettings
from src.domain.chat.models import Chat
from src.infrastructure.database.sqlalchemy_chat_repository import SqlAlchemyChatRepository


@pytest.mark.asyncio
class TestSqlAlchemyChatRepository:
    """Тесты для SqlAlchemyChatRepository."""

    async def test_create_chat(self, test_db, test_token):
        """Создание чата."""
        repo = SqlAlchemyTokenRepository(test_db)
        chat_repo = SqlAlchemyChatRepository(test_db)
        
        chat = Chat(
            token_id=test_token.id,
            name="Test Chat",
            temperature=0.7
        )
        
        created = await chat_repo.create(chat)
        
        assert created.chat_id is not None
        assert created.name == "Test Chat"
        assert created.token_id == test_token.id

    async def test_get_by_id(self, test_db, test_chat):
        """Получение чата по ID."""
        repo = SqlAlchemyChatRepository(test_db)
        
        found = await repo.get_by_id(test_chat.id)
        
        assert found is not None
        assert found.chat_id == test_chat.id

    async def test_get_by_id_not_found(self, test_db):
        """Получение несуществующего чата."""
        repo = SqlAlchemyChatRepository(test_db)
        
        found = await repo.get_by_id(UUID(int=0))
        
        assert found is None

    async def test_get_by_token_id_and_chat_id(self, test_db, test_chat):
        """Получение чата по token_id и chat_id."""
        repo = SqlAlchemyChatRepository(test_db)
        
        found = await repo.get_by_token_id_and_chat_id(
            test_chat.token_id,
            test_chat.id
        )
        
        assert found is not None
        assert found.chat_id == test_chat.id

    async def test_list_by_token_id(self, test_db, test_chat):
        """Получение списка чатов токена."""
        repo = SqlAlchemyChatRepository(test_db)
        
        chats = await repo.list_by_token_id(test_chat.token_id, limit=10, offset=0)
        
        assert len(chats) >= 1
        assert any(c.chat_id == test_chat.id for c in chats)

    async def test_update_chat(self, test_db, test_chat):
        """Обновление чата."""
        repo = SqlAlchemyChatRepository(test_db)
        
        chat = await repo.get_by_id(test_chat.id)
        chat.name = "Updated Chat"
        
        updated = await repo.update(chat)
        
        assert updated is not None
        assert updated.name == "Updated Chat"

    async def test_delete_chat(self, test_db, test_chat):
        """Удаление чата."""
        repo = SqlAlchemyChatRepository(test_db)
        
        await repo.delete(test_chat.id)
        
        found = await repo.get_by_id(test_chat.id)
        assert found is None

    async def test_count_sessions(self, test_db, test_session):
        """Подсчёт количества сессий у чата."""
        repo = SqlAlchemyChatRepository(test_db)
        
        count = await repo.count_sessions(test_session.chat_id)
        
        assert count >= 1

    async def test_count_by_model_id(self, test_db, test_chat):
        """Подсчёт количества чатов для модели."""
        repo = SqlAlchemyChatRepository(test_db)
        
        count = await repo.count_by_model_id(test_chat.model_id or 0)
        
        assert count >= 0
