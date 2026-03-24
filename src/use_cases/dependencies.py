"""
Зависимости для внедрения use cases.

Все зависимости строятся по принципу:
1. get_db() → AsyncSession
2. get_*_repository(db) → Repository
3. get_*_use_case(repository) → UseCase
4. Роутеры используют только use cases через Depends
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal
from src.infrastructure.database.sqlalchemy_chat_repository import SqlAlchemyChatRepository
from src.infrastructure.database.sqlalchemy_message_repository import SqlAlchemyMessageRepository
from src.infrastructure.database.sqlalchemy_model_repository import SqlAlchemyModelRepository
from src.domain.llm_model.repositories import ModelRepository
from src.infrastructure.database.sqlalchemy_session_repository import SqlAlchemySessionRepository
from src.infrastructure.database.sqlalchemy_token_repository import SqlAlchemyTokenRepository
from src.use_cases.auth_service import AuthService

# ============================================================================
# Use Case импорты
# ============================================================================
from src.use_cases.token.create import CreateTokenUseCase, CreateTokenInput, CreateTokenOutput
from src.use_cases.token.get import GetTokenUseCase, GetTokenInput, GetTokenOutput
from src.use_cases.token.update import UpdateTokenUseCase, UpdateTokenInput, UpdateTokenOutput
from src.use_cases.token.delete import DeleteTokenUseCase, DeleteTokenInput, DeleteTokenOutput
from src.use_cases.token.list import ListTokensUseCase, ListTokensInput

from src.use_cases.chat.create import CreateChatUseCase, CreateChatInput
from src.use_cases.chat.get import GetChatUseCase, GetChatInput
from src.use_cases.chat.list import ListChatsUseCase, ListChatsInput
from src.use_cases.chat.update import UpdateChatUseCase, UpdateChatInput
from src.use_cases.chat.delete import DeleteChatUseCase, DeleteChatInput

from src.use_cases.session.create import CreateSessionUseCase, CreateSessionInput, CreateSessionOutput
from src.use_cases.session.get import GetSessionUseCase, GetSessionInput, GetSessionOutput
from src.use_cases.session.list import ListSessionsUseCase, ListSessionsInput, ListSessionsOutput
from src.use_cases.session.delete import DeleteSessionUseCase, DeleteSessionInput, DeleteSessionOutput
from src.use_cases.session.update import UpdateSessionUseCase, UpdateSessionInput, UpdateSessionOutput

from src.use_cases.message.get import GetMessagesUseCase, GetMessagesInput, GetMessagesOutput

from src.use_cases.model.create import CreateModelUseCase
from src.use_cases.model.get import GetModelUseCase
from src.use_cases.model.list import ListModelsUseCase
from src.use_cases.model.update import UpdateModelUseCase
from src.use_cases.model.delete import DeleteModelUseCase

from src.use_cases.llm.ask import LLMAskUseCase
from src.use_cases.llm.stream import LLMStreamUseCase
from src.use_cases.llm.single import LLMSingleUseCase
from src.domain.utils.token_counter import TokenCounter
from src.infrastructure.llm.orchestrator import LLMOrchestratorImpl
from src.infrastructure.llm.providers.factory import get_provider_factory


# ============================================================================
# Базовые зависимости
# ============================================================================

async def get_db() -> AsyncSession:
    """Зависимость для получения сессии БД."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_auth_service() -> AuthService:
    """Зависимость для AuthService."""
    from src.core.config import settings
    return AuthService(auth_url=settings.AUTH_SERVICE_URL)


# ============================================================================
# Репозитории
# ============================================================================

async def get_token_repository(db: AsyncSession = Depends(get_db)) -> SqlAlchemyTokenRepository:
    """Зависимость для TokenRepository."""
    return SqlAlchemyTokenRepository(db)


async def get_chat_repository(db: AsyncSession = Depends(get_db)) -> SqlAlchemyChatRepository:
    """Зависимость для ChatRepository."""
    return SqlAlchemyChatRepository(db)


async def get_session_repository(db: AsyncSession = Depends(get_db)) -> SqlAlchemySessionRepository:
    """Зависимость для SessionRepository."""
    return SqlAlchemySessionRepository(db)


async def get_message_repository(db: AsyncSession = Depends(get_db)) -> SqlAlchemyMessageRepository:
    """Зависимость для MessageRepository."""
    return SqlAlchemyMessageRepository(db)


async def get_model_repository(db: AsyncSession = Depends(get_db)) -> SqlAlchemyModelRepository:
    """Зависимость для ModelRepository."""
    return SqlAlchemyModelRepository(db)


# ============================================================================
# Token Use Cases
# ============================================================================

async def get_create_token_use_case(
    token_repository: SqlAlchemyTokenRepository = Depends(get_token_repository),
    chat_repository: SqlAlchemyChatRepository = Depends(get_chat_repository),
) -> CreateTokenUseCase:
    """Зависимость для CreateTokenUseCase."""
    return CreateTokenUseCase(
        token_repository=token_repository,
        chat_repository=chat_repository,
    )


async def get_token_use_case(
    token_repository: SqlAlchemyTokenRepository = Depends(get_token_repository)
) -> GetTokenUseCase:
    """Зависимость для GetTokenUseCase."""
    return GetTokenUseCase(token_repository)


async def get_update_token_use_case(
    token_repository: SqlAlchemyTokenRepository = Depends(get_token_repository)
) -> UpdateTokenUseCase:
    """Зависимость для UpdateTokenUseCase."""
    return UpdateTokenUseCase(token_repository)


async def get_delete_token_use_case(
    token_repository: SqlAlchemyTokenRepository = Depends(get_token_repository)
) -> DeleteTokenUseCase:
    """Зависимость для DeleteTokenUseCase."""
    return DeleteTokenUseCase(token_repository)


async def get_list_tokens_use_case(
    token_repository: SqlAlchemyTokenRepository = Depends(get_token_repository)
) -> ListTokensUseCase:
    """Зависимость для ListTokensUseCase."""
    return ListTokensUseCase(token_repository)


# ============================================================================
# Chat Use Cases
# ============================================================================

async def get_create_chat_use_case(
    chat_repository: SqlAlchemyChatRepository = Depends(get_chat_repository)
) -> CreateChatUseCase:
    """Зависимость для CreateChatUseCase."""
    return CreateChatUseCase(chat_repository)


async def get_chat_use_case(
    chat_repository: SqlAlchemyChatRepository = Depends(get_chat_repository)
) -> GetChatUseCase:
    """Зависимость для GetChatUseCase."""
    return GetChatUseCase(chat_repository)


async def get_list_chats_use_case(
    chat_repository: SqlAlchemyChatRepository = Depends(get_chat_repository)
) -> ListChatsUseCase:
    """Зависимость для ListChatsUseCase."""
    return ListChatsUseCase(chat_repository)


async def get_update_chat_use_case(
    chat_repository: SqlAlchemyChatRepository = Depends(get_chat_repository)
) -> UpdateChatUseCase:
    """Зависимость для UpdateChatUseCase."""
    return UpdateChatUseCase(chat_repository)


async def get_delete_chat_use_case(
    chat_repository: SqlAlchemyChatRepository = Depends(get_chat_repository)
) -> DeleteChatUseCase:
    """Зависимость для DeleteChatUseCase."""
    return DeleteChatUseCase(chat_repository)


# ============================================================================
# Session Use Cases
# ============================================================================

async def get_create_session_use_case(
    session_repository: SqlAlchemySessionRepository = Depends(get_session_repository)
) -> CreateSessionUseCase:
    """Зависимость для CreateSessionUseCase."""
    return CreateSessionUseCase(session_repository)


async def get_session_use_case(
    session_repository: SqlAlchemySessionRepository = Depends(get_session_repository),
    message_repository: SqlAlchemyMessageRepository = Depends(get_message_repository)
) -> GetSessionUseCase:
    """Зависимость для GetSessionUseCase."""
    return GetSessionUseCase(session_repository, message_repository)


async def get_list_sessions_use_case(
    session_repository: SqlAlchemySessionRepository = Depends(get_session_repository),
    message_repository: SqlAlchemyMessageRepository = Depends(get_message_repository)
) -> ListSessionsUseCase:
    """Зависимость для ListSessionsUseCase."""
    return ListSessionsUseCase(session_repository, message_repository)


async def get_delete_session_use_case(
    session_repository: SqlAlchemySessionRepository = Depends(get_session_repository)
) -> DeleteSessionUseCase:
    """Зависимость для DeleteSessionUseCase."""
    return DeleteSessionUseCase(session_repository)


async def get_update_session_use_case(
    session_repository: SqlAlchemySessionRepository = Depends(get_session_repository)
) -> UpdateSessionUseCase:
    """Зависимость для UpdateSessionUseCase."""
    return UpdateSessionUseCase(session_repository)


# ============================================================================
# Message Use Cases
# ============================================================================

async def get_messages_use_case(
    message_repository: SqlAlchemyMessageRepository = Depends(get_message_repository)
) -> GetMessagesUseCase:
    """Зависимость для GetMessagesUseCase."""
    return GetMessagesUseCase(message_repository)


# ============================================================================
# Model Use Cases
# ============================================================================

async def get_create_model_use_case(
    model_repository: ModelRepository = Depends(get_model_repository)
) -> CreateModelUseCase:
    """Зависимость для CreateModelUseCase."""
    return CreateModelUseCase(model_repository)


async def get_model_use_case(
    model_repository: ModelRepository = Depends(get_model_repository)
) -> GetModelUseCase:
    """Зависимость для GetModelUseCase."""
    return GetModelUseCase(model_repository)


async def get_list_models_use_case(
    model_repository: ModelRepository = Depends(get_model_repository)
) -> ListModelsUseCase:
    """Зависимость для ListModelsUseCase."""
    return ListModelsUseCase(model_repository)


async def get_update_model_use_case(
    model_repository: ModelRepository = Depends(get_model_repository)
) -> UpdateModelUseCase:
    """Зависимость для UpdateModelUseCase."""
    return UpdateModelUseCase(model_repository)


async def get_delete_model_use_case(
    model_repository: ModelRepository = Depends(get_model_repository)
) -> DeleteModelUseCase:
    """Зависимость для DeleteModelUseCase."""
    return DeleteModelUseCase(model_repository)


# ============================================================================
# LLM Use Cases
# ============================================================================

async def get_token_counter() -> TokenCounter:
    """Зависимость для TokenCounter."""
    from src.infrastructure.services.token_counter_impl import get_token_counter
    return get_token_counter()


async def get_llm_orchestrator(
    model_repository: ModelRepository = Depends(get_model_repository),
) -> LLMOrchestratorImpl:
    """Зависимость для LLMOrchestrator."""
    return LLMOrchestratorImpl(
        model_repository=model_repository,
        llm_factory=get_provider_factory(),
    )


async def get_llm_ask_use_case(
    token_repository: SqlAlchemyTokenRepository = Depends(get_token_repository),
    session_repository: SqlAlchemySessionRepository = Depends(get_session_repository),
    chat_repository: SqlAlchemyChatRepository = Depends(get_chat_repository),
    message_repository: SqlAlchemyMessageRepository = Depends(get_message_repository),
    orchestrator: LLMOrchestratorImpl = Depends(get_llm_orchestrator),
    token_counter: TokenCounter = Depends(get_token_counter),
) -> LLMAskUseCase:
    """Зависимость для LLMAskUseCase."""
    return LLMAskUseCase(
        token_repository=token_repository,
        session_repository=session_repository,
        chat_repository=chat_repository,
        message_repository=message_repository,
        orchestrator=orchestrator,
        token_counter=token_counter,
    )


async def get_llm_stream_use_case(
    token_repository: SqlAlchemyTokenRepository = Depends(get_token_repository),
    session_repository: SqlAlchemySessionRepository = Depends(get_session_repository),
    chat_repository: SqlAlchemyChatRepository = Depends(get_chat_repository),
    message_repository: SqlAlchemyMessageRepository = Depends(get_message_repository),
    orchestrator: LLMOrchestratorImpl = Depends(get_llm_orchestrator),
    token_counter: TokenCounter = Depends(get_token_counter),
) -> LLMStreamUseCase:
    """Зависимость для LLMStreamUseCase."""
    return LLMStreamUseCase(
        token_repository=token_repository,
        session_repository=session_repository,
        chat_repository=chat_repository,
        message_repository=message_repository,
        orchestrator=orchestrator,
        token_counter=token_counter,
    )


async def get_llm_single_use_case(
    token_repository: SqlAlchemyTokenRepository = Depends(get_token_repository),
    chat_repository: SqlAlchemyChatRepository = Depends(get_chat_repository),
    model_repository: ModelRepository = Depends(get_model_repository),
    token_counter: TokenCounter = Depends(get_token_counter),
) -> LLMSingleUseCase:
    """Зависимость для LLMSingleUseCase."""
    return LLMSingleUseCase(
        token_repository=token_repository,
        chat_repository=chat_repository,
        model_repository=model_repository,
        token_counter=token_counter,
    )

