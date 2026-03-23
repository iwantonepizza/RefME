#!/usr/bin/env python3
"""
Скрипт для применения миграций Alembic при запуске контейнера.
"""

import sys
import time

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text

from src.core.config import settings


def wait_for_db(engine, max_retries=30, retry_delay=2):
    """Ждём пока БД станет доступна."""
    print(f"⏳ Waiting for database connection...")
    
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("✅ Database connection established")
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️  Attempt {attempt + 1}/{max_retries} failed: {e}")
                print(f"⏳ Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"❌ Could not connect to database after {max_retries} attempts")
                return False
    
    return False


def get_current_revision(engine) -> str | None:
    """Получить текущую ревизию базы данных."""
    try:
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            return context.get_current_revision()
    except Exception as e:
        print(f"⚠️  Could not get current revision: {e}")
        return None


def get_head_revision(alembic_cfg: Config) -> str:
    """Получить последнюю ревизию из миграций."""
    script = ScriptDirectory.from_config(alembic_cfg)
    return script.get_current_head()


def run_migrations():
    """Применить миграции к базе данных."""
    print("=" * 60)
    print("🔄 Starting database migrations...")
    print("=" * 60)

    # Создаём конфиг Alembic
    alembic_cfg = Config("/app/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    alembic_cfg.set_main_option("script_location", "/app/migrations")

    # Создаём sync engine для миграций
    db_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
    engine = create_engine(db_url, echo=False)

    try:
        # Ждём пока БД станет доступна
        if not wait_for_db(engine):
            print("❌ Database is not available. Exiting...")
            sys.exit(1)

        # Проверяем текущую и целевую ревизии
        current_rev = get_current_revision(engine)
        head_rev = get_head_revision(alembic_cfg)

        print(f"📊 Current revision: {current_rev or 'None (empty database)'}")
        print(f"📊 Head revision: {head_rev}")

        if current_rev == head_rev:
            print("✅ Database is up to date")
            return True

        # Применяем миграции
        print("🚀 Applying migrations...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations applied successfully")
        
        # Проверяем что применилось
        new_rev = get_current_revision(engine)
        print(f"📊 New revision: {new_rev}")
        
        return True

    except Exception as e:
        print(f"❌ Migration error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        engine.dispose()


if __name__ == "__main__":
    success = run_migrations()
    if not success:
        sys.exit(1)
