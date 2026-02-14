from typing import List, Dict, Tuple, Any
from sentence_transformers import CrossEncoder
import structlog

log = structlog.get_logger()

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:
    """
    Cross-encoder reranking для улучшения релевантности.
    Использует CPU-модель, не требует GPU.
    """

    def __init__(self):
        self._model: CrossEncoder | None = None

    def _get_model(self) -> CrossEncoder:
        if self._model is None:
            self._model = CrossEncoder(RERANKER_MODEL)
        return self._model

    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Ранжирует документы по релевантности к запросу.
        Возвращает список (документ, оценка) от наиболее релевантного к наименее.
        """
        if not documents:
            return []
            
        model = self._get_model()
        
        # Подготавливаем пары (query, document_text)
        pairs = []
        for doc in documents:
            text = f"{doc.get('name', '')} {doc.get('description', '')}"
            pairs.append((query, text))
        
        # Получаем оценки
        scores = model.predict(pairs)
        
        # Создаем список с оценками
        scored_docs = [
            (doc, float(score))
            for doc, score in zip(documents, scores)
        ]
        
        # Сортируем по оценке и берем top_k
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs[:top_k]