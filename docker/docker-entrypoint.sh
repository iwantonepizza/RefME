#!/bin/bash
set -e

echo "Starting LLM Gateway..."

# Применяем миграции
echo "Running database migrations..."
python /app/run_migrations.py

# Запускаем приложение
echo "Starting application..."
exec "$@"
