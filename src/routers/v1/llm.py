"""
Роутер для запросов к LLM.
"""

from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from src.core.config import settings
from src.core.logging import logger
from src.core.rate_limiter import limiter
from src.database.api_token import APIToken
from src.infrastructure.utils.api_tokens import get_llm_api_token_from_headers
from src.infrastructure.services.token_converter import TokenConverter
from src.use_cases.dependencies import (
    get_llm_ask_use_case,
    get_llm_stream_use_case,
    get_llm_single_use_case,
)
from src.use_cases.llm.ask import LLMAskUseCase, LLMAskInput
from src.use_cases.llm.stream import LLMStreamUseCase, LLMStreamInput
from src.use_cases.llm.single import LLMSingleUseCase, LLMSingleUseCaseInput

router = APIRouter(
    tags=["LLM"],
)


@router.post("/ask")
async def llm_endpoint(
    request: Request,
    session_id: UUID,
    msg_text: Annotated[str | None, Form()] = None,
    role: Annotated[str, Form()] = "user",
    images: Annotated[
        List[UploadFile | None], File(description="Изображения (опционально)",
                                         json_schema_extra={"nullable": True})
    ] = None,
    api_llm_token: APIToken = Depends(get_llm_api_token_from_headers),
    use_case: LLMAskUseCase = Depends(get_llm_ask_use_case),
):
    """
    Запрос к LLM по API токену + session_id.

    Поддерживает отправку изображений для мультимодальных моделей.
    """
    # Конвертируем ORM модель в domain модель
    domain_token = TokenConverter.to_domain(api_llm_token)

    input_data = LLMAskInput(
        api_token=domain_token,
        session_id=session_id,
        msg_text=msg_text,
        role=role,
        images=images,
    )

    result = await use_case.execute(input_data)

    return {"response": result.response, "latency": result.latency, "session_id": result.session_id}


@router.post("/stream")
async def llm_stream_endpoint(
    request: Request,
    session_id: UUID,
    msg_text: Annotated[str | None, Form()] = None,
    role: Annotated[str, Form()] = "user",
    images: List[UploadFile | None] = File(default=None),
    api_llm_token: APIToken = Depends(get_llm_api_token_from_headers),
    use_case: LLMStreamUseCase = Depends(get_llm_stream_use_case),
):
    """
    Поточный ответ от LLM по API токену + session_id (с историей).

    Поддерживает мультимодальные запросы с изображениями.
    Возвращает stream как text/event-stream.
    """
    # Конвертируем ORM модель в domain модель
    domain_token = TokenConverter.to_domain(api_llm_token)

    input_data = LLMStreamInput(
        api_token=domain_token,
        session_id=session_id,
        msg_text=msg_text,
        role=role,
        images=images,
    )

    # Для streaming вызываем _run_logic напрямую (не через execute)
    return StreamingResponse(
        use_case._run_logic(input_data),
        media_type="text/event-stream"
    )


@router.post("/single")
async def llm_single_no_history(
    request: Request,
    chat_id: UUID,
    msg_text: Annotated[str | None, Form()] = None,
    role: Annotated[str, Form()] = "user",
    images: List[UploadFile | None] = File(default=None),
    api_llm_token: APIToken = Depends(get_llm_api_token_from_headers),
    use_case: LLMSingleUseCase = Depends(get_llm_single_use_case),
):
    """
    Сингл запрос без истории сообщений (без session_id и без чтения/записи сообщений в БД).

    Отправляет запрос в нативный Ollama /api/chat.
    Поддерживает мультимодальные запросы.
    """
    # Конвертируем ORM модель в domain модель
    domain_token = TokenConverter.to_domain(api_llm_token)

    input_data = LLMSingleUseCaseInput(
        api_token=domain_token,
        chat_id=chat_id,
        msg_text=msg_text,
        role=role,
        images=images,
    )

    result = await use_case.execute(input_data)

    return {"response": result.response, "latency": result.latency, "chat_id": result.chat_id}
