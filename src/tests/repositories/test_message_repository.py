"""
Тесты для MessageRepository.
"""

import pytest
from src.database.message import ChatMessage
from src.domain.message.models import Message
from src.core.constants import MessageStatus, Role
from src.infrastructure.database.sqlalchemy_message_repository import SqlAlchemyMessageRepository


@pytest.mark.asyncio
class TestSqlAlchemyMessageRepository:
    """Тесты для SqlAlchemyMessageRepository."""

    async def test_create_message(self, test_db, test_session):
        """Создание сообщения."""
        repo = SqlAlchemyMessageRepository(test_db)
        
        message = Message(
            role=Role.USER,
            content="Test message",
            status=MessageStatus.COMPLETED,
            session_id=test_session.id
        )
        
        created = await repo.create(message)
        
        assert created.message_id is not None
        assert created.content == "Test message"
        assert created.role == Role.USER

    async def test_get_by_session_id(self, test_db, test_message):
        """Получение сообщений по session_id."""
        repo = SqlAlchemyMessageRepository(test_db)
        
        messages = await repo.get_by_session_id(test_message.session_id, limit=10, offset=0)
        
        assert len(messages) >= 1
        assert any(m.message_id == test_message.id for m in messages)

    async def test_get_by_session_id_empty(self, test_db, test_session):
        """Получение сообщений из пустой сессии."""
        repo = SqlAlchemyMessageRepository(test_db)
        
        messages = await repo.get_by_session_id(test_session.id, limit=10, offset=0)
        
        assert len(messages) == 0

    async def test_get_by_id(self, test_db, test_message):
        """Получение сообщения по ID."""
        repo = SqlAlchemyMessageRepository(test_db)
        
        found = await repo.get_by_id(test_message.id)
        
        assert found is not None
        assert found.message_id == test_message.id

    async def test_get_by_id_not_found(self, test_db):
        """Получение несуществующего сообщения."""
        from uuid import UUID
        repo = SqlAlchemyMessageRepository(test_db)
        
        found = await repo.get_by_id(UUID(int=0))
        
        assert found is None

    async def test_update_message(self, test_db, test_message):
        """Обновление сообщения."""
        repo = SqlAlchemyMessageRepository(test_db)
        
        message = await repo.get_by_id(test_message.id)
        message.content = "Updated message"
        
        updated = await repo.update(message)
        
        assert updated is not None
        assert updated.content == "Updated message"

    async def test_delete_message(self, test_db, test_message):
        """Удаление сообщения."""
        repo = SqlAlchemyMessageRepository(test_db)
        
        await repo.delete(test_message.id)
        
        found = await repo.get_by_id(test_message.id)
        assert found is None
