"""
Роутер для управления чатами.
Все ручки требуют авторизации через Bearer токен.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from src.core.logging import logger
from src.infrastructure.utils.auth import get_current_user
from src.schemas.chat_schemas import (
    ChatCreateSchema,
    ChatUpdateSchema,
    ChatResponseSchema,
    ChatListResponseSchema,
    DeleteResponseSchema,
)
from src.use_cases.dependencies import (
    get_create_chat_use_case,
    get_chat_use_case,
    get_list_chats_use_case,
    get_update_chat_use_case,
    get_delete_chat_use_case,
)
from src.use_cases.chat.create import CreateChatUseCase, CreateChatInput
from src.use_cases.chat.get import GetChatUseCase, GetChatInput
from src.use_cases.chat.list import ListChatsUseCase, ListChatsInput
from src.use_cases.chat.update import UpdateChatUseCase, UpdateChatInput
from src.use_cases.chat.delete import DeleteChatUseCase, DeleteChatInput

router = APIRouter(
    tags=["Chats"],
    dependencies=[Depends(get_current_user)],
    prefix="/tokens/{token_id}/chats",
)


@router.post("/", summary="Создать чат", response_model=ChatResponseSchema)
async def create_chat(
    token_id: int = Path(..., description="ID API токена"),
    chat_data: ChatCreateSchema | None = None,
    use_case: CreateChatUseCase = Depends(get_create_chat_use_case),
):
    """
    Создание нового чата.

    - **name**: название чата (опционально)
    - **model_id**: ID модели из справочника (опционально)
    - **system_prompt**: системный промпт (опционально)
    - **temperature**: температура генерации (опционально)
    - **max_tokens**: максимум токенов (опционально)
    - **context_window**: размер контекстного окна (опционально)
    """
    logger.info(f"Запрос на создание чата для токена ID={token_id}")

    input_data = CreateChatInput(
        token_id=token_id,
        **(chat_data.model_dump() if chat_data else {}),
    )

    return await use_case.execute(input_data)


@router.get("/", summary="Список чатов токена", response_model=ChatListResponseSchema)
async def list_chats(
    token_id: int = Path(..., description="ID API токена"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    use_case: ListChatsUseCase = Depends(get_list_chats_use_case),
):
    """
    Получение всех чатов токена с пагинацией.

    - **limit**: максимальное количество записей
    - **offset**: смещение для пагинации
    """
    logger.info(f"Запрос на получение списка чатов для токена ID={token_id}")

    input_data = ListChatsInput(token_id=token_id, limit=limit, offset=offset)
    return await use_case.execute(input_data)


@router.get("/{chat_id}", summary="Получить чат", response_model=ChatResponseSchema)
async def get_chat(
    token_id: int = Path(..., description="ID API токена"),
    chat_id: UUID = Path(..., description="ID чата"),
    use_case: GetChatUseCase = Depends(get_chat_use_case),
):
    """Получение чата по ID токена + ID чата."""
    logger.info(f"Запрос на получение чата {chat_id}")

    input_data = GetChatInput(token_id=token_id, chat_id=chat_id)
    return await use_case.execute(input_data)


@router.delete("/{chat_id}", summary="Удалить чат", response_model=DeleteResponseSchema)
async def delete_chat(
    token_id: int = Path(..., description="ID API токена"),
    chat_id: UUID = Path(..., description="ID чата"),
    use_case: DeleteChatUseCase = Depends(get_delete_chat_use_case),
):
    """Удаление чата по ID токена + ID чата."""
    logger.info(f"Запрос на удаление чата {chat_id}")

    input_data = DeleteChatInput(token_id=token_id, chat_id=chat_id)
    return await use_case.execute(input_data)


@router.put("/{chat_id}", summary="Обновить чат", response_model=ChatResponseSchema)
async def update_chat(
    token_id: int = Path(..., description="ID API токена"),
    chat_id: UUID = Path(..., description="ID чата"),
    data: ChatUpdateSchema = ...,
    use_case: UpdateChatUseCase = Depends(get_update_chat_use_case),
):
    """
    Обновление данных чата по ID токена + ID чата.

    - **name**: название чата
    - **system_prompt**: системный промпт (макс. 32000 символов)
    - **model_id**: ID модели из справочника
    - **temperature**: температура генерации
    - **max_tokens**: максимум токенов
    - **context_window**: размер контекстного окна
    """
    logger.info(f"Запрос на обновление чата {chat_id}")

    input_data = UpdateChatInput(
        token_id=token_id,
        chat_id=chat_id,
        **data.model_dump(),
    )
    return await use_case.execute(input_data)
