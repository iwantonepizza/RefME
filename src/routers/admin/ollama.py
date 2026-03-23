"""
Админский роутер для получения информации от Ollama.
"""

import httpx
from fastapi import APIRouter, Depends, HTTPException

from src.core.config import settings
from src.core.logging import logger
from src.infrastructure.llm.providers.ollama import OllamaProvider
from src.infrastructure.llm.providers.vllm import VLLMProvider

router = APIRouter(
    tags=["Admin Control"],
)


@router.get("/ollama/models")
async def get_ollama_models():
    """
    Получение списка моделей из Ollama.

    Возвращает все модели установленные в Ollama сервере.
    """
    logger.info("Запрос списка моделей из Ollama")

    try:
        provider = OllamaProvider(base_url=settings.OLLAMA_URL)
        models = await provider.get_available_models()

        return {
            "status": "success",
            "provider": "ollama",
            "url": settings.OLLAMA_URL,
            "models": models,
            "count": len(models),
        }
    except Exception as e:
        logger.error(f"Ошибка получения моделей из Ollama: {e}")
        raise HTTPException(status_code=503, detail=f"Ollama недоступна: {str(e)}")


@router.get("/ollama/models/{model_name}")
async def get_ollama_model_info(model_name: str):
    """
    Получение информации о конкретной модели из Ollama.
    """
    logger.info(f"Запрос информации о модели {model_name}")

    try:
        provider = OllamaProvider(base_url=settings.OLLAMA_URL)
        info = await provider.get_model_info(model_name)

        return {
            "status": "success",
            "provider": "ollama",
            "model": model_name,
            "info": info,
        }
    except Exception as e:
        logger.error(f"Ошибка получения информации о модели: {e}")
        raise HTTPException(status_code=503, detail=f"Ollama недоступна: {str(e)}")


@router.get("/vllm/models")
async def get_vllm_models():
    """
    Получение списка моделей из vLLM.
    """
    logger.info("Запрос списка моделей из vLLM")

    if not settings.VLLM_URL:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "vllm_not_configured",
                "message": "vLLM URL не настроен. Проверьте переменную окружения VLLM_URL",
            }
        )

    try:
        provider = VLLMProvider(
            base_url=settings.VLLM_URL,
            api_key=settings.VLLM_API_KEY,
        )
        models = await provider.get_available_models()

        return {
            "status": "success",
            "provider": "vllm",
            "url": settings.VLLM_URL,
            "models": models,
            "count": len(models),
        }
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "vllm_unavailable",
                "message": f"vLLM сервер недоступен по адресу {settings.VLLM_URL}",
                "hint": "Проверьте что vLLM запущен и доступен",
            }
        )
    except Exception as e:
        logger.error(f"Ошибка получения моделей из vLLM: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "vllm_error",
                "message": f"Ошибка при получении моделей: {str(e)}",
            }
        )
