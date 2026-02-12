FROM python:3.12-slim

WORKDIR /app

# Установка зависимостей
COPY pyproject.toml .
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --only main

# Копирование кода
COPY src/ src/

# Экспорт переменных окружения
ENV PYTHONPATH=/app/src

# Запуск Celery worker и FastAPI
CMD ["sh", "-c", "celery -A src.tasks.celery_app worker --loglevel=info & uvicorn src.main:app --host 0.0.0.0 --port 8006"]