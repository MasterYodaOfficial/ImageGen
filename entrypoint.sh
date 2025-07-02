#!/bin/bash
set -e

cd /bot

export PYTHONPATH=/bot

echo "📦 Применение миграций Alembic..."
alembic upgrade head

echo "🚀 Запуск Telegram-бота..."
python bot/main.py
