"""
Настройка логирования.
"""

import logging
import os
import sys

from src.core.logging.filter import ServiceNameFilter

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Формат логов
LOG_FORMAT = "%(asctime)s | %(levelname)s | pid %(process)d | %(filename)s:%(lineno)d | %(message)s"

# Настраиваем базовое логирование
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Создаём logger для сервиса
logger = logging.getLogger(__name__)
logger.addFilter(ServiceNameFilter("LLM Gateway"))
