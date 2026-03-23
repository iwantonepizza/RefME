"""
Утилиты для парсинга запросов.
"""

import json
from typing import Optional

from src.schemas.llm_schemas import RequestModelSchema


def parse_request_field(msg: Optional[str] = None, role: str = "user") -> RequestModelSchema:
    """
    Парсинг полей формы в RequestModelSchema.

    :param msg: Текст сообщения (может быть JSON строкой)
    :param role: Роль пользователя
    :return: RequestModelSchema
    """
    # Если msg - JSON строка, парсим её
    if msg and msg.strip().startswith("{"):
        try:
            data = json.loads(msg)
            return RequestModelSchema(msg=data.get("msg"), role=data.get("role", "user"), images=data.get("images"))
        except json.JSONDecodeError:
            pass

    # Иначе используем как простой текст
    return RequestModelSchema(msg=msg, role=role)
