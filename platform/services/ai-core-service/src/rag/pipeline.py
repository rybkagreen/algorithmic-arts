from typing import Dict, Any
from .retriever import HybridRetriever
from .reranker import Reranker
from ..llm.router import LLMRouter

# Константы из промпта
CONTEXT_WINDOW = 6000  # символов (не токенов)
TOP_K_RETRIEVER = 20
TOP_K_RERANKER = 5


class RAGPipeline:
    """
    RAG пайплайн: retrieve → rerank → generate.
    """

    def __init__(
        self,
        retriever: HybridRetriever,
        reranker: Reranker,
        llm_router: LLMRouter,
        system_prompt: str = ""
    ):
        self.retriever = retriever
        self.reranker = reranker
        self.llm_router = llm_router
        self.system_prompt = system_prompt

    async def run(
        self,
        query: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Запускает полный RAG пайплайн.
        Возвращает результат с контекстом и генерацией.
        """
        if context is None:
            context = {}

        # 1. Retrieve
        retrieved_docs = await self.retriever.retrieve(query, context.get("session"), top_k=TOP_K_RETRIEVER)
        
        # 2. Rerank
        reranked_docs = await self.reranker.rerank(query, retrieved_docs, top_k=TOP_K_RERANKER)
        
        # 3. Prepare context
        context_text = ""
        for doc, score in reranked_docs:
            doc_text = f"Компания: {doc.get('name', '')}\n"
            doc_text += f"Индустрия: {doc.get('industry', '')}\n"
            doc_text += f"Описание: {doc.get('description', '')}\n"
            doc_text += f"Технологии: {', '.join(doc.get('tech_stack', []))}\n"
            doc_text += f"Схожесть: {score:.3f}\n\n"
            
            # Проверяем длину контекста
            if len(context_text) + len(doc_text) > CONTEXT_WINDOW:
                break
            context_text += doc_text
        
        # 4. Generate
        final_prompt = f"Контекст:\n{context_text}\n\nВопрос: {query}"
        
        try:
            response = await self.llm_router.generate(
                prompt=final_prompt,
                system=self.system_prompt
            )
            return {
                "content": response.content,
                "provider": response.provider,
                "model": response.model,
                "usage": response.usage,
                "latency_ms": response.latency_ms,
                "retrieved_docs": [doc for doc, _ in reranked_docs],
                "context_used": context_text
            }
        except Exception as e:
            return {
                "error": str(e),
                "retrieved_docs": [doc for doc, _ in reranked_docs],
                "context_used": context_text
            }