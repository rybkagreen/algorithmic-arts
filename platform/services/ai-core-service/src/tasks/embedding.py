from celery_app import celery_app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from embeddings.embedding_service import EmbeddingService
from redis.asyncio import Redis

# Инициализация зависимостей
engine = create_async_engine("postgresql+asyncpg://ai_core:password@postgres:5432/ai_core")
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
redis_client = Redis.from_url("redis://redis:6379/0")
embedding_service = EmbeddingService(redis_client)


@celery_app.task(name="ai_core.generate_missing_embeddings")
def generate_missing_embeddings() -> dict:
    """Генерирует эмбеддинги для компаний без embedding."""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def run_embedding():
            async with async_session() as session:
                # Получаем компании без embedding
                result = await session.execute(text("""
                    SELECT id, name, COALESCE(description, '') AS text
                    FROM companies
                    WHERE embedding IS NULL AND deleted_at IS NULL
                    LIMIT 100
                """))
                companies = [dict(r._mapping) for r in result.fetchall()]
                
                if not companies:
                    return {"status": "success", "processed": 0}
                
                # Генерируем эмбеддинги
                texts = [f"{c['name']} {c['text']}" for c in companies]
                embeddings = await embedding_service.embed_batch(texts)
                
                # Обновляем БД
                updates = []
                for i, (company, embedding) in enumerate(zip(companies, embeddings)):
                    updates.append({
                        "id": str(company["id"]),
                        "embedding": str(embedding)
                    })
                
                for update in updates:
                    await session.execute(text("""
                        UPDATE companies 
                        SET embedding = :embedding 
                        WHERE id = :id
                    """), update)
                
                await session.commit()
                
                return {
                    "status": "success",
                    "processed": len(companies),
                    "errors": []
                }
        
        result = loop.run_until_complete(run_embedding())
        return result
    except Exception as exc:
        return {"status": "error", "error": str(exc)}