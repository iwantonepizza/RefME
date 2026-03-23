"""
Конфигурация тестов и фикстуры.
"""

import asyncio
from typing import AsyncGenerator, Generator
import uuid

import pytest
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Импортируем и настраиваем UUID компилятор для SQLite ДО импорта Base
from sqlalchemy.dialects import sqlite
from sqlalchemy import TypeDecorator
from sqlalchemy.dialects.sqlite import CHAR

class UUIDCompiler:
    """Компилятор UUID типа для SQLite."""
    def process(self, element, **kw):
        return "CHAR(36)"

# Регистрируем компилятор
sqlite.base.SQLiteTypeCompiler.visit_UUID = lambda self, *args, **kwargs: "CHAR(36)"

from src.core.config import settings
from src.database.base_model import Base
from src.database.api_token import APIToken
from src.database.chat import ChatSettings
from src.database.session import ChatSession
from src.database.message import ChatMessage
from src.database.llm_model import LLMModel
from src.core.database import AsyncSessionLocal, get_async_session
from src.main import app
from src.use_cases.dependencies import get_db
from src.tests.auth_helper import get_auth_headers, AuthTokenError

# URL тестовой базы данных (SQLite in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Мок для сервиса авторизации
MOCK_AUTH_SERVICE_URL = "http://test-auth-service/validate"
MOCK_USER_ID = 12345

# Флаг для переключения между реальной и мок-авторизацией
USE_REAL_AUTH = False  # Отключаем реальную авторизацию для тестов


@pytest.fixture(scope="session")
def session_auth_token() -> str:
    """Фикстура для получения токена авторизации на уровне сессии."""
    # Всегда используем мок для тестов
    return "mock_user_token_12345"


@pytest.fixture(scope="session", autouse=True)
def setup_test_settings():
    """Настройка тестовых параметров."""
    # Сохраняем оригинальный URL и подменяем на тестовый
    original_url = settings.AUTH_SERVICE_URL
    settings.AUTH_SERVICE_URL = MOCK_AUTH_SERVICE_URL

    yield

    # Восстанавливаем оригинальный URL
    settings.AUTH_SERVICE_URL = original_url


@pytest.fixture(scope="function", autouse=True)
def mock_auth_service():
    """Мок для AuthService в тестах."""
    from src.use_cases.auth_service import AuthService
    original_init = AuthService.__init__
    
    def mock_init(self, auth_url=None):
        original_init(self, auth_url=MOCK_AUTH_SERVICE_URL)
    
    AuthService.__init__ = mock_init
    yield
    AuthService.__init__ = original_init


@pytest.fixture(scope="function")
async def test_engine():
    """Создание тестового движка БД."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Создание тестовой сессии БД."""
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture(scope="function")
async def client(test_db: AsyncSession, mock_respx, test_token: APIToken) -> AsyncGenerator[AsyncClient, None]:
    """Создание тестового HTTP клиента."""
    from datetime import datetime, timezone
    from src.domain.token.models import Token
    
    # Используем test_token вместо создания нового
    domain_token = Token(
        token_id=test_token.id,
        token_value=test_token.token,
        active=test_token.active,
        created_at=test_token.created_at,
        expires_at=test_token.expires_at,
        last_used_at=test_token.last_used_at,
    )
    
    # Сохраняем токен в test_db для использования другими фикстурами
    test_db.llm_token = test_token

    async def override_get_db():
        yield test_db

    async def override_get_async_session():
        yield test_db

    async def override_get_llm_api_token():
        # Возвращаем domain модель (создана выше)
        return domain_token

    # Переопределяем UnitOfWork чтобы использовал тестовую сессию
    from src.infrastructure.database.unitOfWork import SqlAlchemyUnitOfWork
    original_uow_init = SqlAlchemyUnitOfWork.__init__
    original_uow_enter = SqlAlchemyUnitOfWork.__aenter__
    
    def override_uow_init(self, session=None):
        original_uow_init(self, session=test_db)
    
    async def override_uow_enter(self):
        self.session = test_db
        return self
    
    SqlAlchemyUnitOfWork.__init__ = override_uow_init
    SqlAlchemyUnitOfWork.__aenter__ = override_uow_enter

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_async_session] = override_get_async_session

    # Переопределяем get_llm_api_token_from_headers для LLM endpoints
    from src.infrastructure.utils.api_tokens import get_llm_api_token_from_headers
    app.dependency_overrides[get_llm_api_token_from_headers] = override_get_llm_api_token

    # Отключаем rate limiter для тестов
    app.state.limiter = None

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="function", autouse=True)
def mock_respx():
    """Фикстура для мокирования HTTP запросов."""
    import respx

    with respx.mock as mock:
        # Мок для сервиса авторизации - валидация токена
        # Возвращаем MOCK_USER_ID для любого валидного токена
        mock.post(MOCK_AUTH_SERVICE_URL).mock(return_value=Response(200, json=MOCK_USER_ID))
        yield mock


@pytest.fixture
async def test_token(test_db: AsyncSession) -> APIToken:
    """Создание тестового API токена."""
    token = APIToken(token="test_token_12345", active=True)
    test_db.add(token)
    await test_db.commit()
    await test_db.refresh(token)
    return token


@pytest.fixture
async def test_token_inactive(test_db: AsyncSession) -> APIToken:
    """Создание неактивного тестового API токена."""
    token = APIToken(token="inactive_token", active=False)
    test_db.add(token)
    await test_db.commit()
    await test_db.refresh(token)
    return token


@pytest.fixture
async def test_chat(test_db: AsyncSession, test_token: APIToken) -> ChatSettings:
    """Создание тестового чата."""
    # Используем токен из client фикстуры если есть (для LLM тестов)
    # Иначе используем test_token
    token_id = getattr(test_db, 'llm_token', test_token).id if hasattr(test_db, 'llm_token') else test_token.id
    chat = ChatSettings(
        token_id=token_id, model_name="test-model", temperature=0.7, max_tokens=4096, context_window=8192
    )
    test_db.add(chat)
    await test_db.commit()
    await test_db.refresh(chat)
    return chat


@pytest.fixture
async def test_session(test_db: AsyncSession, test_token: APIToken, test_chat: ChatSettings) -> ChatSession:
    """Создание тестовой сессии."""
    # Используем токен из client фикстуры если есть (для LLM тестов)
    # Иначе используем test_token
    token_value = getattr(test_db, 'llm_token', test_token).token if hasattr(test_db, 'llm_token') else test_token.token
    session = ChatSession(token_id=token_value, chat_id=test_chat.id)
    test_db.add(session)
    await test_db.commit()
    await test_db.refresh(session)
    return session


@pytest.fixture
async def test_session_with_deleted_chat(
    test_db: AsyncSession, test_token: APIToken
) -> ChatSession:
    """Создание тестовой сессии с удалённым чатом (chat_id есть, но чат не существует)."""
    # Создаём временный чат и удаляем его
    chat = ChatSettings(token_id=test_token.id, model_name="temp-model")
    test_db.add(chat)
    await test_db.commit()
    await test_db.refresh(chat)

    # Создаём сессию с этим chat_id
    session = ChatSession(token_id=test_token.token, chat_id=chat.id)
    test_db.add(session)
    await test_db.commit()

    # "Удаляем" чат (мягкое удаление)
    chat.deleted_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    await test_db.commit()
    await test_db.refresh(session)

    return session


@pytest.fixture
async def test_message(test_db: AsyncSession, test_session: ChatSession) -> ChatMessage:
    """Создание тестового сообщения."""
    message = ChatMessage(session_id=test_session.id, role="user", content="Test message")
    test_db.add(message)
    await test_db.commit()
    await test_db.refresh(message)
    return message


@pytest.fixture
async def test_model(test_db: AsyncSession) -> LLMModel:
    """Создание тестовой модели."""
    model = LLMModel(
        name="Test Model",
        provider_model="test-model:7b",
        types=["text"],
        provider="ollama",
        active=True,
        temperature=0.7,
    )
    test_db.add(model)
    await test_db.commit()
    await test_db.refresh(model)
    return model


@pytest.fixture
def headers_with_auth(session_auth_token: str) -> dict:
    """Заголовки с токеном авторизации."""
    return {"Authorization": f"Bearer {session_auth_token}", "Content-Type": "application/json"}


@pytest.fixture
def headers_with_api_token(test_token: APIToken) -> dict:
    """Заголовки с API токеном."""
    return {"api-token": test_token.token, "Content-Type": "application/json"}
