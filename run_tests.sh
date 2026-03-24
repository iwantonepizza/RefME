#!/bin/bash
# Скрипт для настройки и запуска тестов

set -e

echo "🚀 Настройка тестового окружения..."

# Шаг 1: Запуск PostgreSQL
echo "📦 Запуск PostgreSQL..."
docker-compose -f docker/docker-compose.yml up -d db

# Ожидание пока БД станет доступна
echo "⏳ Ожидание готовности БД..."
sleep 5

# Шаг 2: Создание тестовой БД
echo "🗄️  Создание тестовой БД..."
docker-compose -f docker/docker-compose.yml exec -T db psql -U llm_user -d llm_gateway -tc "SELECT 1 FROM pg_database WHERE datname = 'llm_gateway_test'" | grep -q 1 || \
docker-compose -f docker/docker-compose.yml exec -T db psql -U llm_user -d llm_gateway -c "CREATE DATABASE llm_gateway_test;"

# Шаг 3: Экспорт переменной окружения
export TEST_DATABASE_URL="postgresql+asyncpg://llm_user:super_pass@localhost:5432/llm_gateway_test"
echo "✅ TEST_DATABASE_URL установлен"

# Шаг 4: Запуск тестов
echo "🧪 Запуск тестов..."
python3 -m pytest src/tests/ -v --tb=short

echo "✅ Тесты завершены!"
