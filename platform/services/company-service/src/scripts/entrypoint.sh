#!/bin/bash
set -e

# Установка прав на выполнение
chmod +x /app/src/scripts/start_projection_worker.py

# Проверка аргументов и запуск соответствующего процесса
case "$1" in
    "projection-worker")
        echo "Starting company projection worker..."
        exec python /app/src/scripts/start_projection_worker.py
        ;;
    "uvicorn")
        echo "Starting uvicorn server..."
        exec uvicorn src.main:app --host 0.0.0.0 --port 8003
        ;;
    *)
        # По умолчанию запускаем основной сервис
        if [ "$1" = "" ]; then
            echo "No command specified, starting default uvicorn server..."
            exec uvicorn src.main:app --host 0.0.0.0 --port 8003
        else
            # Запускаем переданную команду
            exec "$@"
        fi
        ;;
esac