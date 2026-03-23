"""
Настройки подключения к базе данных.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings

logger = logging.getLogger(__name__)

# Создаём движок с настройками connection pool для production
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
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
