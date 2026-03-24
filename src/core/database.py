"""
Настройки подключения к базе данных.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings

logger = logging.getLogger(__name__)

# Создаём движок с настройками connection pool для production
# Параметры pool оптимизированы для production нагрузки:
# - pool_size=20: Базовое количество соединений в пуле (хватает для 20-50 RPS)
# - max_overflow=40: Дополнительные соединения при пиковой нагрузке (всего 60)
# - pool_pre_ping=True: Проверка соединения перед использованием (защита от разрывов)
# - pool_recycle=3600: Пересоздание соединений через 1 час (защита от stale connections)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Отключить логирование SQL запросов (включить для отладки)
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session():
    """Dependency для получения сессии БД с автоматическим commit/rollback."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
            logger.debug("Сессия БД закоммичена")
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка сессии БД, выполнен rollback: {e}")
            raise
        finally:
            await session.close()
