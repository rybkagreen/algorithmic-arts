#!/bin/bash
# Инициализация проекта ALGORITHMIC ARTS

set -e

echo "🚀 Инициализация ALGORITHMIC ARTS..."

# Создаем .env файл из шаблона
if [ ! -f ".env" ]; then
    echo "Copying .env.example to .env..."
    cp .env.example .env
else
    echo ".env already exists, skipping copy"
fi

# Генерируем секреты
if grep -q "REPLACE_ME" .env; then
    echo "Generating secrets..."
    python scripts/generate_secrets.py >> .env
    # Удаляем временные строки с REPLACE_ME
    sed -i '/REPLACE_ME/d' .env
else
    echo "Secrets already generated, skipping"
fi

# Создаем директории для данных
mkdir -p data/{uploads,reports,backups}

# Создаем директории для логов
mkdir -p logs/{platform,postgres,redis,kafka}

echo "✅ Инициализация завершена. Отредактируйте .env перед запуском."