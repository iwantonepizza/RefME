"""
Исключения типа "уже существует" (409).
"""

from src.exceptions.domain_exceptions.base import DomainException


class AlreadyExistsError(DomainException):
    """Сущность уже существует."""
    status_code = 409
    error_code = "ALREADY_EXISTS"

    def __init__(self, entity_name: str, field_name: str, field_value: str | int):
        self.field_name = field_name
        self.field_value = field_value
        self.entity_name = entity_name
        self.message = (
            f"Сущность '{entity_name}' со значением '{field_value}' "
            f"поля '{field_name}' уже существует"
        )
        super().__init__(self.message)


class ModelAlreadyExistsError(AlreadyExistsError):
    """Модель уже существует."""

    def __init__(self, model_name: str):
        super().__init__("Модель", "name", model_name)
