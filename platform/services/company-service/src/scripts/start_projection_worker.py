#!/usr/bin/env python3
"""
Запуск Kafka projection worker для обновления read models (Elasticsearch).
Этот скрипт запускается как отдельный процесс в Docker.
"""

import asyncio
import structlog
import sys
from pathlib import Path

# Добавляем корневую директорию в sys.path для импорта модулей
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.elasticsearch.company_indexer import CompanyIndexer
from infrastructure.kafka.consumers import CompanyProjectionWorker
from config import settings
from elasticsearch import AsyncElasticsearch

logger = structlog.get_logger()


async def main():
    """Основная функция запуска projection worker."""
    logger.info("starting_company_projection_worker")
    
    try:
        # Инициализация зависимостей
        es_client = AsyncElasticsearch(
            hosts=[settings.ELASTICSEARCH_URL],
            http_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD),
            timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )
        
        indexer = CompanyIndexer(es_client)
        worker = CompanyProjectionWorker(es_client, indexer)
        
        # Запуск worker
        await worker.start()
        logger.info("company_projection_worker_running")
        
        # Ожидание завершения (работает бесконечно)
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("shutdown_requested")
    except Exception as e:
        logger.error("projection_worker_startup_failed", error=str(e))
        raise
    finally:
        if 'worker' in locals():
            await worker.stop()
        if 'es_client' in locals():
            await es_client.close()


if __name__ == "__main__":
    asyncio.run(main())