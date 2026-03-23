"""
Базовый класс для CRUD Use Cases.

Устраняет дублирование CRUD операций в use cases.
Использует паттерн Template Method.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.use_cases.base_use_case import BaseUseCase

# Типы для CRUD операций
TEntity = TypeVar('TEntity')  # Domain entity
TCreate = TypeVar('TCreate')  # Схема создания
TUpdate = TypeVar('TUpdate')  # Схема обновления
TOutput = TypeVar('TOutput')  # Выходная схема
TId = TypeVar('TId')  # Тип ID (int, UUID, etc)


class BaseCRUDUseCase(ABC, Generic[TEntity, TCreate, TUpdate, TOutput, TId]):
    """
    Базовый класс для CRUD Use Cases.

    Предоставляет стандартные CRUD операции:
    - create()
    - get()
    - update()
    - delete()

    Наследники должны реализовать абстрактные методы.
    """

    @abstractmethod
    async def _create_entity(self, input_data: TCreate) -> TEntity:
        """Создание entity."""
        pass

    @abstractmethod
    async def _get_entity(self, id: TId) -> TEntity:
        """Получение entity."""
        pass

    @abstractmethod
    async def _update_entity(self, id: TId, input_data: TUpdate) -> TEntity:
        """Обновление entity."""
        pass

    @abstractmethod
    async def _delete_entity(self, id: TId) -> None:
        """Удаление entity."""
        pass

    @abstractmethod
    def _to_output(self, entity: TEntity) -> TOutput:
        """Конвертация entity в output схему."""
        pass

    async def create(self, input_data: TCreate) -> TOutput:
        """
        Создание entity.

        :param input_data: Входные данные
        :return: Output схема
        """
        entity = await self._create_entity(input_data)
        return self._to_output(entity)

    async def get(self, id: TId) -> TOutput:
        """
        Получение entity.

        :param id: ID entity
        :return: Output схема
        """
        entity = await self._get_entity(id)
        return self._to_output(entity)

    async def update(self, id: TId, input_data: TUpdate) -> TOutput:
        """
        Обновление entity.

        :param id: ID entity
        :param input_data: Входные данные
        :return: Output схема
        """
        entity = await self._update_entity(id, input_data)
        return self._to_output(entity)

    async def delete(self, id: TId) -> dict:
        """
        Удаление entity.

        :param id: ID entity
        :return: Результат удаления
        """
        await self._delete_entity(id)
        return {"success": True, "message": "Entity deleted"}
