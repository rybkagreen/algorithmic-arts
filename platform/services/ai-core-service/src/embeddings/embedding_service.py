import hashlib
import json
from redis.asyncio import Redis
from sentence_transformers import SentenceTransformer
import structlog

log = structlog.get_logger()

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
EMBEDDING_DIM = 768
CACHE_TTL = 86400  # 24 часа


class EmbeddingService:
    """
    Генерирует 768-мерные эмбеддинги через sentence-transformers.
    Кэшируем по SHA-256 хэшу текста (TTL 24ч).
    Поддерживает batch-обработку.
    """

    def __init__(self, redis: Redis):
        self.redis = redis
        self._model: SentenceTransformer | None = None

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(MODEL_NAME)
        return self._model

    @staticmethod
    def _cache_key(text: str) -> str:
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        return f"embed:{h}"

    async def embed(self, text: str) -> list[float]:
        """Одиночный эмбеддинг с кэшем."""
        key = self._cache_key(text)
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)

        model = self._get_model()
        vector = model.encode(text, normalize_embeddings=True).tolist()
        await self.redis.setex(key, CACHE_TTL, json.dumps(vector))
        return vector

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Batch-эмбеддинг: сначала пробуем кэш,
        остальные считаем в один вызов модели.
        """
        keys = [self._cache_key(t) for t in texts]
        cached_values = await self.redis.mget(*keys)

        missing_indices = [
            i for i, val in enumerate(cached_values) if val is None
        ]
        missing_texts = [texts[i] for i in missing_indices]

        if missing_texts:
            model = self._get_model()
            new_vectors = model.encode(
                missing_texts, normalize_embeddings=True, batch_size=32
            ).tolist()
            pipe = self.redis.pipeline()
            for idx, vec in zip(missing_indices, new_vectors):
                pipe.setex(keys[idx], CACHE_TTL, json.dumps(vec))
            await pipe.execute()
        else:
            new_vectors = []

        result = []
        new_iter = iter(new_vectors)
        for i, val in enumerate(cached_values):
            if val is not None:
                result.append(json.loads(val))
            else:
                result.append(next(new_iter))

        log.info("embeddings_generated",
                 total=len(texts),
                 from_cache=len(texts) - len(missing_texts),
                 computed=len(missing_texts))
        return result