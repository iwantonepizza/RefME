"""
Админский роутер для управления LLM моделями.
Все ручки требуют авторизации через Bearer токен.
"""


from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query

from src.core.logging import logger
from src.infrastructure.utils.auth import get_current_user
from src.schemas.admin.model_schemas import ModelCreateSchema, ModelUpdateSchema
from src.use_cases.dto import ModelDTO, ModelListDTO
from src.use_cases.dependencies import (
    get_create_model_use_case,
    get_model_use_case,
    get_list_models_use_case,
    get_update_model_use_case,
    get_delete_model_use_case,
)
from src.use_cases.model.create import CreateModelUseCase, CreateModelInput
from src.use_cases.model.get import GetModelUseCase, GetModelInput
from src.use_cases.model.list import ListModelsUseCase, ListModelsInput
from src.use_cases.model.update import UpdateModelUseCase, UpdateModelInput
from src.use_cases.model.delete import DeleteModelUseCase, DeleteModelInput

router = APIRouter(
    tags=["Admin Models"],
    dependencies=[Depends(get_current_user)],
)


# ==================== CRUD ручки ====================


@router.get("/", response_model=ModelListDTO)
async def list_models(
    show_inactive: bool = Query(default=False, description="Показывать неактивные модели"),
    limit: int | None = Query(default=100, ge=1, le=1000),
    offset: int | None = Query(default=0, ge=0),
    use_case: ListModelsUseCase = Depends(get_list_models_use_case),
):
    """
    Получение всех моделей из справочника.

    - **show_inactive**: если True, показывает и неактивные модели
    - **limit**: максимальное количество записей
    - **offset**: смещение для пагинации
    """
    logger.info(f"Админский запрос на получение моделей (show_inactive={show_inactive})")

    input_data = ListModelsInput(
        active_only=not show_inactive,
        limit=limit,
        offset=offset,
    )
    return await use_case.execute(input_data)


@router.get("/{model_id}", response_model=ModelDTO)
async def get_model(
    model_id: int = Path(..., description="ID модели"),
    use_case: GetModelUseCase = Depends(get_model_use_case),
):
    """Получение модели по ID с полной информацией."""
    logger.info(f"Админский запрос на получение модели {model_id}")

    try:
        input_data = GetModelInput(model_id=model_id)
        return await use_case.execute(input_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=ModelDTO)
async def create_model(
    model_data: ModelCreateSchema,
    use_case: CreateModelUseCase = Depends(get_create_model_use_case),
):
    """
    Создание новой модели в справочнике.

    - **name**: человекочитаемое название
    - **provider_model**: имя модели у провайдера (Ollama)
    - **type**: тип модели (text, image, multimodal)
    - **active**: активна ли модель
    - **max_tokens**: лимит токенов
    - **context_window**: размер контекста
    - **temperature**: температура по умолчанию
    - **description**: описание
    """
    logger.info(f"Админский запрос на создание модели {model_data.provider_model}")

    try:
        input_data = CreateModelInput(
            name=model_data.name,
            provider_model=model_data.provider_model,
            types=[model_data.type],  # Конвертируем type (str) в types (list)
            provider=model_data.provider,
            active=model_data.active,
            temperature=model_data.temperature,
            max_tokens=model_data.max_tokens,
            context_window=model_data.context_window,
            description=model_data.description,
        )
        return await use_case.execute(input_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{model_id}", response_model=ModelDTO)
async def update_model(
    model_id: int = Path(..., description="ID модели"),
    model_data: ModelUpdateSchema = ...,
    use_case: UpdateModelUseCase = Depends(get_update_model_use_case),
):
    """
    Обновление параметров модели.

    Можно обновить: name, active, max_tokens, context_window, temperature, description
    """
    logger.info(f"Админский запрос на обновление модели {model_id}")

    try:
        input_data = UpdateModelInput(
            model_id=model_id,
            name=model_data.name,
            provider_model=model_data.provider_model,
            active=model_data.active,
            temperature=model_data.temperature,
            max_tokens=model_data.max_tokens,
            context_window=model_data.context_window,
            description=model_data.description,
        )
        return await use_case.execute(input_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{model_id}")
async def delete_model(
    model_id: int = Path(..., description="ID модели"),
    use_case: DeleteModelUseCase = Depends(get_delete_model_use_case),
):
    """
    Удаление модели (мягкое - через active=False).

    Модель не удаляется физически, а помечается как неактивная.
    """
    logger.info(f"Админский запрос на удаление модели {model_id}")

    try:
        input_data = DeleteModelInput(model_id=model_id)
        await use_case.execute(input_data)
        return {"success": True, "message": "Модель выключена"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
