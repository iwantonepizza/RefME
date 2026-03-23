"""
Роутер для управления сессиями.

Роутер не обрабатывает исключения — это делают глобальные handlers.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query

from src.core.logging import logger
from src.use_cases.dependencies import (
    get_create_session_use_case,
    get_session_use_case,
    get_list_sessions_use_case,
    get_delete_session_use_case,
    get_messages_use_case,
    get_update_session_use_case,
    get_token_use_case,
)
from src.use_cases.session.create import CreateSessionUseCase, CreateSessionInput
from src.use_cases.session.get import GetSessionUseCase, GetSessionInput
from src.use_cases.session.list import ListSessionsUseCase, ListSessionsInput
from src.use_cases.session.delete import DeleteSessionUseCase, DeleteSessionInput
from src.use_cases.session.update import UpdateSessionUseCase, UpdateSessionInput
from src.use_cases.message.get import GetMessagesUseCase, GetMessagesInput
from src.use_cases.token.get import GetTokenUseCase, GetTokenInput

router = APIRouter(
    tags=["Sessions"],
    prefix="/tokens/{token_id}/sessions",
)


async def _get_token_value(
    token_id: int,
    use_case: GetTokenUseCase = Depends(get_token_use_case),
) -> str:
    """Получение значения токена по ID через Use Case."""
    result = await use_case.execute(GetTokenInput(token_id=token_id))
    return result.token_value


@router.post("/", summary="Создать сессию")
async def create_session(
    token_id: int = Path(..., description="ID API токена"),
    chat_id: UUID = ...,
    use_case: CreateSessionUseCase = Depends(get_create_session_use_case),
    token_value: str = Depends(_get_token_value),
):
    """
    Создание новой сессии.

    - **chat_id**: ID чата для привязки

    При создании сессии автоматически сохраняется system_prompt чата как первое сообщение.
    """
    logger.info(f"Запрос на создание сессии для токена ID={token_id}")

    result = await use_case.execute(CreateSessionInput(
        token_id=token_value,
        chat_id=chat_id,
    ))
    return {"session_id": result.session_id}


@router.get("/", summary="Все сессии чата")
async def get_sessions(
    token_id: int = Path(..., description="ID API токена"),
    chat_id: UUID = ...,
    use_case: ListSessionsUseCase = Depends(get_list_sessions_use_case),
    token_value: str = Depends(_get_token_value),
):
    """
    Получение всех сессий чата.
    """
    logger.info(f"Запрос на получение списка сессий для токена ID={token_id}")

    result = await use_case.execute(ListSessionsInput(
        token_id=token_value,
        limit=None,
        offset=0,
    ))

    # Фильтруем по chat_id на уровне приложения
    items = [item for item in result.items if item.chat_id == chat_id]

    return {"items": items}


@router.get("/{session_id}", summary="Получение сессии")
async def get_session(
    token_id: int = Path(..., description="ID API токена"),
    session_id: UUID = Path(..., description="ID сессии"),
    use_case: GetSessionUseCase = Depends(get_session_use_case),
    token_value: str = Depends(_get_token_value),
):
    """
    Получение сессии по ID.
    """
    logger.info(f"Запрос на получение сессии: {session_id}")

    return await use_case.execute(GetSessionInput(
        token_id=token_value,
        session_id=session_id,
    ))


@router.delete("/{session_id}", summary="Удалить сессию")
async def delete_session(
    token_id: int = Path(..., description="ID API токена"),
    session_id: UUID = Path(..., description="ID сессии"),
    use_case: DeleteSessionUseCase = Depends(get_delete_session_use_case),
    token_value: str = Depends(_get_token_value),
):
    """
    Удаление сессии по ID.
    """
    logger.info(f"Удаление сессии {session_id}")

    await use_case.execute(DeleteSessionInput(
        token_id=token_value,
        session_id=session_id,
    ))
    return {"detail": "Сессия удалена"}


@router.get("/{session_id}/messages", summary="Сообщения сессии")
async def get_session_messages(
    session_id: UUID = Path(..., description="ID сессии"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    use_case: GetMessagesUseCase = Depends(get_messages_use_case),
):
    """
    Получение сообщений сессии с пагинацией.

    - **limit**: максимальное количество записей
    - **offset**: смещение для пагинации
    """
    return await use_case.execute(GetMessagesInput(
        session_id=session_id,
        limit=limit,
        offset=offset,
    ))


@router.put("/{session_id}/chat", summary="Перепривязать сессию к другому чату")
async def reassign_session_to_chat(
    session_id: UUID = Path(..., description="ID сессии"),
    chat_id: UUID = ...,
    use_case: UpdateSessionUseCase = Depends(get_update_session_use_case),
):
    """
    Перепривязка сессии к другому чату.

    - **chat_id**: ID нового чата
    """
    logger.info(f"Запрос на перепривязку сессии {session_id} к чату {chat_id}")

    result = await use_case.execute(UpdateSessionInput(
        session_id=session_id,
        chat_id=chat_id,
    ))

    logger.info(f"Сессия {session_id} перепривязана к чату {chat_id}")
    return {"success": result.success, "session_id": result.session_id, "chat_id": result.chat_id}
