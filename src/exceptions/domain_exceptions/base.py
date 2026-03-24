"""
Базовый класс для domain исключений.
"""


class DomainException(Exception):
    """
    Базовый класс для domain исключений.

    Все domain исключения наследуются от этого класса.
    Глобальные обработчики преобразуют их в HTTP ответы.
    """
    status_code: int = 500
    error_code: str = "DOMAIN_ERROR"

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
