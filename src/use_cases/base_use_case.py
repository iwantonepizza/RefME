"""
Базовый класс для всех Use Cases.

Использует паттерн Template Method:
- execute() — общий метод с логированием и обработкой ошибок
- _run_logic() — бизнес-логика (переопределяется в наследниках)
- _present() — конвертация domain → output (опционально)
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.core.logging.logging_decorator import logging_decorator

TInput = TypeVar('TInput')
TOutput = TypeVar('TOutput')


class BaseOutput:
    """Базовый класс для всех Output объектов."""
    
    def model_dump(self) -> dict:
        """Конвертация в dict для сериализации."""
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}


class BaseUseCase(ABC, Generic[TInput, TOutput]):
    """
    Базовый класс для всех Use Cases.

    Использует паттерн Template Method:
    - execute() — общий метод с логированием
    - _run_logic() — бизнес-логика (переопределяется в наследниках)
    - _present() — конвертация domain → output (опционально)
    """

    @abstractmethod
    async def _run_logic(self, input_data: TInput) -> TOutput:
        """
        Основная логика Use Case.

        :param input_data: Входные данные
        :return: Результат выполнения
        """
        raise NotImplementedError

    @logging_decorator
    async def execute(self, input_data: TInput) -> TOutput:
        """
        Публичный метод вызова Use Case.

        Автоматически логирует:
        - Вызов use case
        - Время выполнения
        - Ошибки с traceback

        :param input_data: Входные данные
        :return: Результат выполнения
        """
        return await self._run_logic(input_data)

    def _present(self, domain_obj: object) -> TOutput:
        """
        Конвертация domain объекта в output.

        Переопределяется если нужна кастомная логика конвертации.
        По умолчанию пытается вызвать model_validate() или возвращает объект.

        :param domain_obj: Domain объект
        :return: Output объект
        """
        # Пытаемся использовать Pydantic model_validate если есть
        if hasattr(TOutput, 'model_validate'):
            return TOutput.model_validate(domain_obj)
        # Иначе возвращаем как есть (для dataclass)
        return domain_obj
