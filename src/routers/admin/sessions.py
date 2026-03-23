"""
Админский роутер для управления сессиями.
Все ручки требуют авторизации через Bearer токен.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from src.core.logging import logger
from src.exceptions.domain_exceptions import DomainException
from src.infrastructure.utils.auth import get_current_user
from src.use_cases.dependencies import (
    get_session_use_case,
    get_list_sessions_use_case,
    get_delete_session_use_case,
    get_messages_use_case,
)
from src.use_cases.session.get import GetSessionUseCase, GetSessionInput
from src.use_cases.session.list import ListSessionsUseCase, ListSessionsInput
from src.use_cases.session.delete import DeleteSessionUseCase, DeleteSessionInput
from src.use_cases.message.get import GetMessagesUseCase, GetMessagesInput
from src.use_cases.dto import MessageListDTO, PaginationDTO, SessionDTO, SessionListDTO

router = APIRouter(
    tags=["Admin Sessions"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=SessionListDTO)
async def list_all_sessions(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    use_case: ListSessionsUseCase = Depends(get_list_sessions_use_case),
):
    """
    Получение всех сессий в системе (админская ручка).

    - **limit**: максимальное количество записей
    - **offset**: смещение для пагинации
    """
    logger.info("Админский запрос на получение всех сессий")

    # Получаем все сессии через use case
    # Для админки используем пустой token_id чтобы получить все
    input_data = ListSessionsInput(token_id="", limit=limit, offset=offset)
    result = await use_case.execute(input_data)

    return SessionListDTO(
        items=[
            SessionDTO(
                id=item.session_id,
                token_id=item.token_id,
                chat_id=item.chat_id,
                created_at=item.created_at
            ) for item in result.items
        ],
        pagination=PaginationDTO(limit=limit, offset=offset, total=result.total),
    )


@router.get("/{session_id}", response_model=SessionDTO)
async def get_session(
    session_id: UUID = Path(..., description="ID сессии"),
    use_case: GetSessionUseCase = Depends(get_session_use_case),
):
    """Получение сессии по ID (админская ручка)."""
    logger.info(f"Админский запрос на получение сессии {session_id}")

    try:
        # Для админки используется пустой токен
        input_data = GetSessionInput(token_id="", session_id=session_id)
        result = await use_case.execute(input_data)

        return SessionDTO(
            id=result.session_id,
            token_id=result.token_id,
            chat_id=result.chat_id,
            created_at=result.created_at,
        )
    except DomainException as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка при получении сессии: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка при получении сессии: {str(e)}")


@router.delete("/{session_id}")
async def delete_session(
    session_id: UUID = Path(..., description="ID сессии"),
    use_case: DeleteSessionUseCase = Depends(get_delete_session_use_case),
):
    """Удаление сессии по ID (админская ручка)."""
    logger.info(f"Админский запрос на удаление сессии {session_id}")

    try:
        # Для админки используется пустой токен
        input_data = DeleteSessionInput(token_id="", session_id=session_id)
        await use_case.execute(input_data)
        return {"success": True}
    except DomainException as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка при удалении сессии: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка при удалении сессии: {str(e)}")


@router.get("/token/{token_id}", response_model=SessionListDTO)
async def get_sessions_by_token(
    token_id: int = Path(..., description="ID API токена"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    use_case: ListSessionsUseCase = Depends(get_list_sessions_use_case),
):
    """Получение всех сессий конкретного токена (админская ручка)."""
    logger.info(f"Админский запрос на получение сессий токена ID={token_id}")

    try:
        input_data = ListSessionsInput(token_id=str(token_id), limit=limit, offset=offset)
        result = await use_case.execute(input_data)

        return SessionListDTO(
            items=[
                SessionDTO(
                    id=item.session_id,
                    token_id=item.token_id,
                    chat_id=item.chat_id,
                    created_at=item.created_at,
                ) for item in result.items
            ],
            pagination=PaginationDTO(limit=limit, offset=offset, total=result.total),
        )
    except Exception as e:
        logger.error(f"Ошибка при получении сессий токена: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка при получении списка сессий: {str(e)}")


@router.get("/chat/{chat_id}", response_model=SessionListDTO)
async def get_sessions_by_chat(
    chat_id: UUID = Path(..., description="ID чата"),
    use_case: ListSessionsUseCase = Depends(get_list_sessions_use_case),
):
    """Получение всех сессий конкретного чата (админская ручка)."""
    logger.info(f"Админский запрос на получение сессий чата {chat_id}")

    try:
        # Получаем все сессии и фильтруем по chat_id
        input_data = ListSessionsInput(token_id="", limit=None, offset=0)
        result = await use_case.execute(input_data)

        # Фильтруем по chat_id
        items = [item for item in result.items if item.chat_id == chat_id]

        return SessionListDTO(
            items=[
                SessionDTO(
                    id=item.session_id,
                    token_id=item.token_id,
                    chat_id=item.chat_id,
                    created_at=item.created_at,
                ) for item in items
            ],
            pagination=PaginationDTO(limit=len(items), offset=0, total=len(items)),
        )
    except Exception as e:
        logger.error(f"Ошибка при получении сессий чата: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка при получении списка сессий: {str(e)}")


@router.get("/{session_id}/messages", response_model=MessageListDTO)
async def get_session_messages(
    session_id: UUID = Path(..., description="ID сессии"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    use_case: GetMessagesUseCase = Depends(get_messages_use_case),
):
    """Получение сообщений сессии (админская ручка)."""
    logger.info(f"Админский запрос на получение сообщений сессии {session_id}")

    try:
        input_data = GetMessagesInput(session_id=session_id, limit=limit, offset=offset)
        result = await use_case.execute(input_data)

        # Импортируем MessageDTO здесь чтобы избежать циклического импорта
        from src.use_cases.dto import MessageDTO

        return MessageListDTO(
            items=[
                MessageDTO(
                    id=item.message_id,
                    session_id=item.session_id,
                    role=item.role,
                    content=item.content,
                    status=item.status,
                    process_at=item.started_at,
                    created_at=item.created_at,
                    started_at=item.started_at,
                    completed_at=item.completed_at,
                ) for item in result.items
            ],
            pagination=PaginationDTO(limit=limit, offset=offset, total=result.total),
        )
    except DomainException as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка при получении сообщений: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка при получении сообщений: {str(e)}")
