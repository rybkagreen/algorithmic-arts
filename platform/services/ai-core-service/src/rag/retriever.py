import asyncio
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from .embedding_service import EmbeddingService

# Константы из промпта
RRF_K = 60
TOP_K_RETRIEVER = 20
MAX_BM25_DOCS = 500


class HybridRetriever:
    """
    Гибридный поиск: pgvector (dense) + BM25 (sparse).
    Использует RRF для объединения результатов.
    """

    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.bm25_cache: Dict[str, BM25Okapi] = {}

    async def retrieve(
        self,
        query: str,
        session: AsyncSession,
        top_k: int = TOP_K_RETRIEVER
    ) -> List[Dict[str, Any]]:
        """
        Выполняет гибридный поиск и возвращает top_k документов.
        """
        # Получаем эмбеддинг запроса
        query_embedding = await self.embedding_service.embed(query)
        
        # Запускаем оба поиска параллельно
        dense_results, sparse_results = await asyncio.gather(
            self._dense_search(query_embedding, session, limit=50),
            self._sparse_search(query, session, limit=50)
        )
        
        # Объединяем через RRF
        combined_scores = {}
        for i, doc in enumerate(dense_results):
            doc_id = str(doc["id"])
            score = 1.0 / (RRF_K + i + 1)
            combined_scores[doc_id] = combined_scores.get(doc_id, 0.0) + score
        
        for i, doc in enumerate(sparse_results):
            doc_id = str(doc["id"])
            score = 1.0 / (RRF_K + i + 1)
            combined_scores[doc_id] = combined_scores.get(doc_id, 0.0) + score
        
        # Сортируем по сумме баллов и берем top_k
        sorted_docs = sorted(
            combined_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        # Получаем полные документы по ID
        doc_ids = [doc_id for doc_id, _ in sorted_docs]
        if not doc_ids:
            return []
            
        result = await self._get_documents_by_ids(doc_ids, session)
        return result

    async def _dense_search(
        self, 
        embedding: List[float], 
        session: AsyncSession, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Поиск по pgvector с оператором <=> (cosine)."""
        result = await session.execute(text("""
            SELECT id, name, industry, sub_industries, tech_stack, description,
                   1 - (embedding <=> :emb::vector) AS similarity
            FROM companies
            WHERE deleted_at IS NULL AND embedding IS NOT NULL
            ORDER BY embedding <=> :emb::vector
            LIMIT :limit
        """), {"emb": str(embedding), "limit": limit})
        return [dict(r._mapping) for r in result.fetchall()]

    async def _sparse_search(
        self, 
        query: str, 
        session: AsyncSession, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """BM25 поиск по тексту."""
        # Получаем все компании для BM25 (до MAX_BM25_DOCS)
        result = await session.execute(text("""
            SELECT id, name, COALESCE(description, '') as description
            FROM companies
            WHERE deleted_at IS NULL
            LIMIT :max_docs
        """), {"max_docs": MAX_BM25_DOCS})
        docs = [dict(r._mapping) for r in result.fetchall()]
        
        if not docs:
            return []
        
        # Подготавливаем корпус для BM25
        corpus = [f"{doc['name']} {doc['description']}" for doc in docs]
        bm25 = BM25Okapi([doc.split() for doc in corpus])
        
        # Ищем по запросу
        tokenized_query = query.split()
        scores = bm25.get_scores(tokenized_query)
        
        # Создаем список с оценками
        scored_docs = [
            {
                "id": doc["id"],
                "name": doc["name"],
                "industry": "",
                "sub_industries": [],
                "tech_stack": [],
                "description": doc["description"],
                "similarity": float(score)
            }
            for doc, score in zip(docs, scores)
        ]
        
        # Сортируем и берем top_k
        scored_docs.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_docs[:limit]

    async def _get_documents_by_ids(
        self, 
        doc_ids: List[str], 
        session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Получает полные документы по списку ID."""
        if not doc_ids:
            return []
            
        placeholders = ",".join([f"'{id}'" for id in doc_ids])
        result = await session.execute(text(f"""
            SELECT id, name, industry, sub_industries, tech_stack, description, embedding
            FROM companies
            WHERE id IN ({placeholders}) AND deleted_at IS NULL
        """))
        return [dict(r._mapping) for r in result.fetchall()]