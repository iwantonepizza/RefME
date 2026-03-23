"""
Роутер для управления API токенами.
Все ручки требуют авторизации через Bearer токен.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from src.core.logging import logger
from src.infrastructure.utils.auth import get_current_user
from src.use_cases.dependencies import (
    get_create_token_use_case,
    get_token_use_case,
    get_update_token_use_case,
    get_delete_token_use_case,
    get_list_tokens_use_case,
)
from src.use_cases.token.create import CreateTokenUseCase, CreateTokenInput
from src.use_cases.token.get import GetTokenUseCase, GetTokenInput, GetTokenOutput
from src.use_cases.token.update import UpdateTokenUseCase, UpdateTokenInput, UpdateTokenOutput
from src.use_cases.token.delete import DeleteTokenUseCase, DeleteTokenInput, DeleteTokenOutput
from src.use_cases.token.list import ListTokensUseCase, ListTokensInput

router = APIRouter(
    tags=["Tokens"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", summary="Создать токен")
async def create_token(
    use_case: CreateTokenUseCase = Depends(get_create_token_use_case),
):
    """Создание нового API токена."""
    logger.info("Запрос на создание API токена")
    result = await use_case.execute(CreateTokenInput())
    return result


@router.get("/", summary="Список токенов")
async def get_tokens(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    use_case: ListTokensUseCase = Depends(get_list_tokens_use_case),
):
    """Получение всех API токенов с пагинацией."""
    logger.info("Запрос на получение всех API токенов")
    
    input_data = ListTokensInput(limit=limit, offset=offset)
    return await use_case.execute(input_data)


@router.get("/{token_id}", summary="Получить токен")
async def get_token(
    token_id: int = Path(..., description="ID API токена"),
    use_case: GetTokenUseCase = Depends(get_token_use_case),
):
    """Получение токена по ID."""
    logger.info(f"Запрос на получение API токена ID={token_id}")
    
    result = await use_case.execute(GetTokenInput(token_id=token_id))
    return result


@router.put("/{token_id}", summary="Обновить токен")
async def update_token(
    token_id: int = Path(..., description="ID API токена"),
    active: bool = Query(..., description="Активен ли токен"),
    use_case: UpdateTokenUseCase = Depends(get_update_token_use_case),
):
    """Обновление статуса токена."""
    logger.info(f"Запрос на обновление API токена ID={token_id}")
    
    result = await use_case.execute(UpdateTokenInput(token_id=token_id, active=active))
    return result


@router.delete("/{token_id}", summary="Удалить токен")
async def delete_token(
    token_id: int = Path(..., description="ID API токена"),
    use_case: DeleteTokenUseCase = Depends(get_delete_token_use_case),
):
    """Удаление токена."""
    logger.info(f"Запрос на удаление API токена ID={token_id}")
    
    result = await use_case.execute(DeleteTokenInput(token_id=token_id))
    return result
