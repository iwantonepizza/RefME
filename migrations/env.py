import asyncio
from logging.config import fileConfig
from typing import AsyncGenerator

from alembic import context
from sqlalchemy import create_engine, engine_from_config, pool

from src.core.config import settings
from src.database.base_model import Base
from src.database.api_token import APIToken
from src.database.chat import ChatSettings
from src.database.session import ChatSession
from src.database.message import ChatMessage
from src.database.llm_model import LLMModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Переопределяем URL базы данных из переменных окружения
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Run migrations with the given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Для синхронных миграций используем sync engine
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url").replace("postgresql+asyncpg", "postgresql"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
