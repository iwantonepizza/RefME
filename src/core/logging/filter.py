"""
Фильтры для логирования.
"""

import logging


class ServiceNameFilter(logging.Filter):
    """
    Фильтр добавляющий имя сервиса в логи.
    
    Использование:
        logger.addFilter(ServiceNameFilter("LLM Gateway"))
    """
    
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name
    
    def filter(self, record):
        record.service_name = self.service_name
        return True


class HealthCheckFilter(logging.Filter):
    """
    Фильтр для suppression health check логов.
    
    Использование:
        logger.addFilter(HealthCheckFilter())
    """
    
    def filter(self, record):
        # Пропускаем health check endpoint логи
        if hasattr(record, 'pathname') and 'health.py' in record.pathname:
            return False
        return True


class RequestFilter(logging.Filter):
    """
    Фильтр добавляющий информацию о запросе.
    """
    
    def filter(self, record):
        # Добавляем request_id если есть
        if not hasattr(record, 'request_id'):
            record.request_id = '-'
        return True
