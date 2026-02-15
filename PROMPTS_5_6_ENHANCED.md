# ALGORITHMIC ARTS — Улучшенные Промпты №5 и №6

**Версия:** 3.1 (Enhanced)
**Дата:** Февраль 2026
**Статус:** Production Ready

> Расширенная версия промптов №5 и №6 из `PROMPTS_FOR_QWEN.md`.
> Добавлены: полная файловая структура, реализации всех LLM-провайдеров,
> Circuit Breaker + exponential backoff, полный AgentState, инструменты (Tools)
> каждого агента, LangGraph граф с conditional edges, RAG pipeline, Celery-задачи
> и A/B-тест промптов. В промпте №6 — реальный код всех 5 scrapers, anti-bot
> меры, NER-экстракция, нормализация, rapidfuzz-дедупликация и мониторинг.

---

## Промпт №5: AI Core Service (Расширенный)

### Задача
Реализовать AI-движок с мультиагентной системой, LLM-роутером с fallback,
RAG-пайплайном и управлением промптами.

### Промпт

```markdown
Создай AI Core Service для платформы ALGORITHMIC ARTS.
Python 3.12, FastAPI 0.115+, LangChain 0.3+, LangGraph 0.2+,
sentence-transformers 3.x, Celery 5.4, Redis Stack 7.4.

═══════════════════════════════════════════════════════════
ЧАСТЬ 1: ФАЙЛОВАЯ СТРУКТУРА
═══════════════════════════════════════════════════════════

services/ai-core-service/
├── pyproject.toml
├── Dockerfile
└── src/
    ├── main.py
    ├── config.py
    │
    ├── llm/
    │   ├── __init__.py
    │   ├── router.py              # LLMRouter: fallback + circuit breaker
    │   ├── providers/
    │   │   ├── base.py            # BaseLLMProvider ABC
    │   │   ├── yandexgpt.py       # YandexGPT 4 Pro
    │   │   ├── gigachat.py        # GigaChat Pro
    │   │   └── openrouter.py      # Claude / GPT-4o fallback
    │   └── prompt_manager.py      # A/B тест промптов, версионирование
    │
    ├── embeddings/
    │   ├── __init__.py
    │   ├── embedding_service.py   # Batch embed + Redis кэш
    │   └── models.py              # Загрузка sentence-transformers
    │
    ├── rag/
    │   ├── __init__.py
    │   ├── retriever.py           # Hybrid: pgvector + BM25
    │   ├── reranker.py            # Cross-encoder reranking
    │   └── pipeline.py            # RAGPipeline: retrieve → rerank → generate
    │
    ├── agents/
    │   ├── __init__.py
    │   ├── base_agent.py          # BaseAgent ABC, AgentState dataclass
    │   ├── scout_agent.py         # Agent 1: Partnership Scout
    │   ├── analyzer_agent.py      # Agent 2: Compatibility Analyzer
    │   ├── writer_agent.py        # Agent 3: Outreach Writer
    │   ├── enricher_agent.py      # Agent 4: Data Enricher
    │   ├── predictor_agent.py     # Agent 5: Analytics Predictor
    │   ├── orchestrator.py        # LangGraph граф всех агентов
    │   └── tools/
    │       ├── company_tools.py   # get_company, search_similar
    │       ├── web_tools.py       # fetch_url, parse_rss
    │       └── db_tools.py        # save_partnership, update_company
    │
    ├── routers/
    │   └── ai.py                  # HTTP эндпоинты
    │
    ├── tasks/
    │   ├── __init__.py
    │   ├── celery_app.py
    │   ├── enrichment.py          # enrich_company_task
    │   ├── scouting.py            # scout_partnerships_task
    │   └── embedding.py           # generate_embeddings_batch
    │
    ├── kafka/
    │   └── consumers.py           # Слушает company.created
    │
    └── metrics/
        └── prometheus.py          # LLM latency, cost, token usage


═══════════════════════════════════════════════════════════
ЧАСТЬ 2: LLM ПРОВАЙДЕРЫ
═══════════════════════════════════════════════════════════

## src/llm/providers/base.py:

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import time


@dataclass
class LLMUsage:
    prompt_tokens:     int
    completion_tokens: int
    total_tokens:      int
    cost_rub:          float   # Стоимость в рублях


@dataclass
class LLMResponse:
    content:  str
    provider: str
    model:    str
    usage:    LLMUsage
    latency_ms: int


class BaseLLMProvider(ABC):
    name: str
    priority: int
    max_tokens: int = 4000
    temperature: float = 0.3
    _fail_count: int = 0
    _circuit_open_until: float = 0.0

    def is_available(self) -> bool:
        """Circuit breaker: не дёргаем провайдер, если он недавно падал."""
        return time.time() > self._circuit_open_until

    def record_failure(self) -> None:
        self._fail_count += 1
        # После 3 ошибок подряд — открываем circuit на 60 секунд
        if self._fail_count >= 3:
            self._circuit_open_until = time.time() + 60
            self._fail_count = 0

    def record_success(self) -> None:
        self._fail_count = 0
        self._circuit_open_until = 0.0

    @abstractmethod
    async def generate(self, prompt: str, system: str = "") -> LLMResponse:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...


## src/llm/providers/yandexgpt.py:

import httpx
import time
import structlog
from .base import BaseLLMProvider, LLMResponse, LLMUsage

log = structlog.get_logger()

YANDEXGPT_COST_PER_1K_TOKENS = 0.06  # рублей за 1000 токенов

class YandexGPTProvider(BaseLLMProvider):
    name = "yandexgpt"
    priority = 1

    def __init__(self, api_key: str, folder_id: str,
                 model: str = "yandexgpt-pro"):
        self._api_key = api_key
        self._folder_id = folder_id
        self._model = model
        self._base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1"

    async def generate(self, prompt: str, system: str = "") -> LLMResponse:
        start = time.time()
        messages = []
        if system:
            messages.append({"role": "system", "text": system})
        messages.append({"role": "user", "text": prompt})

        payload = {
            "modelUri": f"gpt://{self._folder_id}/{self._model}",
            "completionOptions": {
                "stream": False,
                "temperature": self.temperature,
                "maxTokens": self.max_tokens,
            },
            "messages": messages,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self._base_url}/completion",
                json=payload,
                headers={
                    "Authorization": f"Api-Key {self._api_key}",
                    "x-folder-id": self._folder_id,
                },
            )
            resp.raise_for_status()

        data = resp.json()
        result = data["result"]
        content = result["alternatives"][0]["message"]["text"]
        usage_raw = result.get("usage", {})
        usage = LLMUsage(
            prompt_tokens=usage_raw.get("inputTextTokens", 0),
            completion_tokens=usage_raw.get("completionTokens", 0),
            total_tokens=usage_raw.get("totalTokens", 0),
            cost_rub=usage_raw.get("totalTokens", 0) / 1000 * YANDEXGPT_COST_PER_1K_TOKENS,
        )
        return LLMResponse(
            content=content,
            provider=self.name,
            model=self._model,
            usage=usage,
            latency_ms=int((time.time() - start) * 1000),
        )

    async def health_check(self) -> bool:
        try:
            resp = await self.generate("ping", system="Ответь 'pong'")
            return "pong" in resp.content.lower()
        except Exception:
            return False


## src/llm/providers/gigachat.py (краткая реализация):

import httpx, time
from .base import BaseLLMProvider, LLMResponse, LLMUsage

GIGACHAT_COST_PER_1K = 0.05  # рублей

class GigaChatProvider(BaseLLMProvider):
    name = "gigachat"
    priority = 2

    def __init__(self, api_key: str, scope: str = "GIGACHAT_API_CORP",
                 model: str = "GigaChat-Pro"):
        self._api_key = api_key
        self._scope = scope
        self._model = model
        self._access_token: str | None = None
        self._token_expires: float = 0.0

    async def _get_access_token(self) -> str:
        """OAuth2 аутентификация GigaChat."""
        if self._access_token and time.time() < self._token_expires:
            return self._access_token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
                data={"scope": self._scope},
                headers={"Authorization": f"Basic {self._api_key}"},
                verify=False,
            )
            resp.raise_for_status()
            data = resp.json()
            self._access_token = data["access_token"]
            self._token_expires = time.time() + data.get("expires_in", 1800) - 60
        return self._access_token

    async def generate(self, prompt: str, system: str = "") -> LLMResponse:
        start = time.time()
        token = await self._get_access_token()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.post(
                "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                json={"model": self._model, "messages": messages,
                      "temperature": self.temperature, "max_tokens": self.max_tokens},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0,
            )
            resp.raise_for_status()

        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        usage_raw = data.get("usage", {})
        usage = LLMUsage(
            prompt_tokens=usage_raw.get("prompt_tokens", 0),
            completion_tokens=usage_raw.get("completion_tokens", 0),
            total_tokens=usage_raw.get("total_tokens", 0),
            cost_rub=usage_raw.get("total_tokens", 0) / 1000 * GIGACHAT_COST_PER_1K,
        )
        return LLMResponse(content=content, provider=self.name, model=self._model,
                           usage=usage, latency_ms=int((time.time()-start)*1000))

    async def health_check(self) -> bool:
        try:
            await self.generate("ping")
            return True
        except Exception:
            return False


═══════════════════════════════════════════════════════════
ЧАСТЬ 3: LLM ROUTER С CIRCUIT BREAKER
═══════════════════════════════════════════════════════════

## src/llm/router.py:

import asyncio
import time
import structlog
from prometheus_client import Counter, Histogram
from .providers.base import BaseLLMProvider, LLMResponse

log = structlog.get_logger()

llm_calls = Counter("llm_calls_total",
    "Total LLM API calls", ["provider", "status"])
llm_latency = Histogram("llm_latency_seconds",
    "LLM response latency", ["provider"])
llm_cost = Counter("llm_cost_rub_total",
    "Total LLM cost in RUB", ["provider"])


class AllProvidersFailedError(Exception):
    pass


class LLMRouter:
    """
    Роутер с приоритетами, circuit breaker и exponential backoff.

    Порядок: YandexGPT → GigaChat → OpenRouter (Claude / GPT-4o)
    Circuit breaker: после 3 ошибок — пауза 60 сек, потом повтор.
    Exponential backoff: 1 → 2 → 4 сек между попытками одного провайдера.
    """

    BASE_RETRY_DELAY = 1.0   # секунд
    MAX_RETRIES_PER_PROVIDER = 3

    def __init__(self, providers: list[BaseLLMProvider]):
        self._providers = sorted(providers, key=lambda p: p.priority)

    async def generate(
        self,
        prompt: str,
        system: str = "",
        required_provider: str | None = None,
    ) -> LLMResponse:
        providers = self._providers
        if required_provider:
            providers = [p for p in providers if p.name == required_provider]

        errors: dict[str, str] = {}

        for provider in providers:
            if not provider.is_available():
                log.warning("provider_circuit_open", provider=provider.name)
                continue

            for attempt in range(self.MAX_RETRIES_PER_PROVIDER):
                try:
                    start = time.time()
                    response = await provider.generate(prompt, system=system)

                    provider.record_success()
                    llm_calls.labels(provider=provider.name, status="success").inc()
                    llm_latency.labels(provider=provider.name).observe(
                        time.time() - start
                    )
                    llm_cost.labels(provider=provider.name).inc(
                        response.usage.cost_rub
                    )
                    return response

                except Exception as exc:
                    provider.record_failure()
                    llm_calls.labels(provider=provider.name, status="error").inc()
                    errors[provider.name] = str(exc)
                    log.warning("llm_provider_error",
                                provider=provider.name,
                                attempt=attempt + 1,
                                error=str(exc))

                    if attempt < self.MAX_RETRIES_PER_PROVIDER - 1:
                        delay = self.BASE_RETRY_DELAY * (2 ** attempt)
                        await asyncio.sleep(delay)
                    break  # переходим к следующему провайдеру

        raise AllProvidersFailedError(
            f"Все провайдеры недоступны. Ошибки: {errors}"
        )


═══════════════════════════════════════════════════════════
ЧАСТЬ 4: УПРАВЛЕНИЕ ПРОМПТАМИ (A/B-тест)
═══════════════════════════════════════════════════════════

## src/llm/prompt_manager.py:

import random
import json
from dataclasses import dataclass
from redis.asyncio import Redis


@dataclass
class PromptVersion:
    version: str       # "v1", "v2"
    template: str
    weight: float      # Вес для A/B: 0.0–1.0


class PromptManager:
    """
    Версионирование и A/B-тест промптов.
    Шаблоны хранятся в Redis; можно обновить без деплоя.
    """

    def __init__(self, redis: Redis):
        self.redis = redis
        self._local_cache: dict[str, list[PromptVersion]] = {}

    async def get_prompt(
        self,
        prompt_key: str,
        context: dict,
        force_version: str | None = None,
    ) -> tuple[str, str]:
        """
        Возвращает (rendered_prompt, version).
        Если force_version задан — использует его, иначе A/B выбор.
        """
        versions = await self._load_versions(prompt_key)
        if not versions:
            raise ValueError(f"Промпт '{prompt_key}' не найден")

        version = (
            self._find_version(versions, force_version)
            if force_version
            else self._ab_select(versions)
        )

        rendered = version.template.format(**context)
        # Логируем выбор для статистики
        await self.redis.incr(f"prompt_usage:{prompt_key}:{version.version}")
        return rendered, version.version

    async def _load_versions(
        self, prompt_key: str
    ) -> list[PromptVersion]:
        cached = self._local_cache.get(prompt_key)
        if cached:
            return cached

        raw = await self.redis.get(f"prompts:{prompt_key}")
        if not raw:
            return []
        data = json.loads(raw)
        versions = [PromptVersion(**v) for v in data]
        self._local_cache[prompt_key] = versions
        return versions

    @staticmethod
    def _ab_select(versions: list[PromptVersion]) -> PromptVersion:
        """Взвешенный случайный выбор версии промпта."""
        total = sum(v.weight for v in versions)
        r = random.uniform(0, total)
        cumulative = 0.0
        for v in versions:
            cumulative += v.weight
            if r <= cumulative:
                return v
        return versions[-1]

    @staticmethod
    def _find_version(
        versions: list[PromptVersion], name: str
    ) -> PromptVersion:
        for v in versions:
            if v.version == name:
                return v
        raise ValueError(f"Версия '{name}' не найдена")


═══════════════════════════════════════════════════════════
ЧАСТЬ 5: EMBEDDING SERVICE
═══════════════════════════════════════════════════════════

## src/embeddings/embedding_service.py:

import hashlib, json
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


═══════════════════════════════════════════════════════════
ЧАСТЬ 6: MULTI-AGENT СИСТЕМА (LangGraph)
═══════════════════════════════════════════════════════════

## src/agents/base_agent.py:

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass
class AgentState:
    """Глобальное состояние, передаваемое между агентами в LangGraph."""
    # Входные данные
    trigger:          str             # 'company_created' | 'user_request' | 'scheduled'
    company_id:       UUID | None = None
    company_a_id:     UUID | None = None
    company_b_id:     UUID | None = None
    user_id:          UUID | None = None
    outreach_style:   str = "formal"  # 'formal' | 'friendly' | 'technical'

    # Результаты каждого агента
    scout_insights:       list[dict] = field(default_factory=list)
    enriched_company:     dict | None = None
    compatibility_score:  float | None = None
    compatibility_report: dict | None = None
    outreach_message:     str | None = None
    deal_probability:     float | None = None

    # Служебные
    errors:     list[str] = field(default_factory=list)
    should_notify: bool = False


## src/agents/scout_agent.py — Agent 1: Partnership Scout

from langchain.tools import Tool
from ..llm.router import LLMRouter


SCOUT_SYSTEM_PROMPT = """
Ты — Partnership Scout агент платформы ALGORITHMIC ARTS.
Твоя задача: анализировать новости российского B2B SaaS рынка,
выявлять новые компании и потенциальные партнёрства.

Результат верни СТРОГО в JSON:
{
  "found_companies": [{"name": "...", "industry": "...", "website": "..."}],
  "partnership_signals": [{"company_a": "...", "company_b": "...", "reason": "..."}],
  "market_trends": ["..."]
}
"""


class PartnershipScoutAgent:
    """Мониторит VC.ru, Habr Карьера, Rusbase каждые 15 минут."""

    def __init__(self, llm_router: LLMRouter, http_client):
        self.llm = llm_router
        self.http = http_client

    async def run(self, state: AgentState) -> AgentState:
        try:
            news_text = await self._fetch_news()
            response = await self.llm.generate(
                prompt=f"Проанализируй новости и найди партнёрства:\n\n{news_text[:6000]}",
                system=SCOUT_SYSTEM_PROMPT,
            )
            import json
            insights = json.loads(response.content)
            state.scout_insights = insights.get("found_companies", [])
        except Exception as exc:
            state.errors.append(f"scout_agent: {exc}")
        return state

    async def _fetch_news(self) -> str:
        """Агрегирует RSS-фиды VC.ru, Habr, Rusbase."""
        sources = [
            "https://vc.ru/rss/all",
            "https://habr.com/ru/rss/hubs/ru_java/news/",
        ]
        texts = []
        for url in sources:
            try:
                resp = await self.http.get(url, timeout=10)
                texts.append(resp.text[:3000])
            except Exception:
                pass
        return "\n---\n".join(texts)


## src/agents/analyzer_agent.py — Agent 2: Compatibility Analyzer

ANALYZER_SYSTEM_PROMPT = """
Ты — эксперт по B2B SaaS партнёрствам. Дай развёрнутый анализ совместимости двух компаний.
Результат верни СТРОГО в JSON:
{
  "score": 0.82,
  "strengths": ["общая аудитория", "дополняющий функционал"],
  "risks": ["конкуренция в CRM-сегменте"],
  "recommended_type": "integration",
  "pitch_angle": "Предложите интеграцию через API для автоматизации онбординга"
}
"""


class CompatibilityAnalyzerAgent:
    def __init__(self, llm_router: LLMRouter, company_service_client):
        self.llm = llm_router
        self.company_client = company_service_client

    async def run(self, state: AgentState) -> AgentState:
        if not (state.company_a_id and state.company_b_id):
            return state
        try:
            company_a = await self.company_client.get(state.company_a_id)
            company_b = await self.company_client.get(state.company_b_id)
            prompt = (
                f"Компания A: {company_a}\n\n"
                f"Компания B: {company_b}\n\n"
                f"Оцени совместимость и дай рекомендации."
            )
            response = await self.llm.generate(prompt, system=ANALYZER_SYSTEM_PROMPT)
            import json
            report = json.loads(response.content)
            state.compatibility_score  = report.get("score")
            state.compatibility_report = report
            state.should_notify = (state.compatibility_score or 0) > 0.7
        except Exception as exc:
            state.errors.append(f"analyzer_agent: {exc}")
        return state


## src/agents/writer_agent.py — Agent 3: Outreach Writer

WRITER_PROMPTS = {
    "formal": """
Напиши официальное деловое письмо от {sender_company} к {target_company}.
Цель: предложить стратегическое партнёрство.
Аргументы: {match_reasons}
Письмо должно быть 200–300 слов, без лишних формальностей.
Верни только текст письма.
""",
    "friendly": """
Напиши дружелюбное письмо от {sender_company} к {target_company}.
Цель: предложить партнёрство.
Аргументы: {match_reasons}
Тон: неформальный, тёплый, живой. 150–200 слов.
Верни только текст письма.
""",
    "technical": """
Напиши техническое письмо от {sender_company} к {target_company}.
Цель: предложить технологическую интеграцию.
Синергия: {match_reasons}
Акцент на конкретных технических деталях. 250–350 слов.
Верни только текст письма.
""",
}


class OutreachWriterAgent:
    def __init__(self, llm_router: LLMRouter):
        self.llm = llm_router

    async def run(self, state: AgentState) -> AgentState:
        if not state.compatibility_report:
            return state
        try:
            template = WRITER_PROMPTS.get(state.outreach_style, WRITER_PROMPTS["formal"])
            prompt = template.format(
                sender_company="Ваша компания",
                target_company="Компания-партнёр",
                match_reasons=", ".join(
                    state.compatibility_report.get("strengths", [])
                ),
            )
            response = await self.llm.generate(prompt)
            state.outreach_message = response.content
        except Exception as exc:
            state.errors.append(f"writer_agent: {exc}")
        return state


## src/agents/enricher_agent.py — Agent 4: Data Enricher

ENRICHER_SYSTEM_PROMPT = """
Ты — аналитик данных. По информации о компании составь структурированный профиль.
Верни СТРОГО в JSON:
{
  "ai_summary": "Краткое описание 2-3 предложения",
  "ai_tags": ["SaaS", "B2B", "CRM", "API"],
  "industry_refined": "Martech",
  "business_model": "b2b",
  "tech_stack_inferred": {"python": true, "react": true}
}
"""


class DataEnricherAgent:
    def __init__(self, llm_router: LLMRouter):
        self.llm = llm_router

    async def run(self, state: AgentState) -> AgentState:
        if not state.company_id:
            return state
        try:
            # В реальном коде здесь получаем данные компании
            company_data = state.enriched_company or {}
            prompt = (
                f"Обогати данные компании:\n"
                f"Название: {company_data.get('name','')}\n"
                f"Описание: {company_data.get('description','')}\n"
                f"Сайт: {company_data.get('website','')}"
            )
            response = await self.llm.generate(prompt, system=ENRICHER_SYSTEM_PROMPT)
            import json
            enrichment = json.loads(response.content)
            if state.enriched_company:
                state.enriched_company.update(enrichment)
            else:
                state.enriched_company = enrichment
        except Exception as exc:
            state.errors.append(f"enricher_agent: {exc}")
        return state


## src/agents/predictor_agent.py — Agent 5: Analytics Predictor

import numpy as np

class AnalyticsPredictorAgent:
    """
    Предсказывает вероятность закрытия сделки.
    Используем простую эвристическую модель (в продакшене — GradientBoosting).
    """

    FEATURE_WEIGHTS = {
        "compatibility_score":    0.35,
        "both_verified":          0.20,
        "same_city":              0.10,
        "has_api":                0.15,
        "funding_stage_match":    0.20,
    }

    async def run(self, state: AgentState) -> AgentState:
        try:
            score = state.compatibility_score or 0.0
            features = {
                "compatibility_score": score,
                "both_verified":       1.0 if score > 0.7 else 0.0,
                "same_city":           0.8,  # TODO: из реальных данных
                "has_api":             1.0,
                "funding_stage_match": 0.7,
            }
            probability = sum(
                v * self.FEATURE_WEIGHTS[k] for k, v in features.items()
            )
            state.deal_probability = round(min(probability, 1.0), 4)
        except Exception as exc:
            state.errors.append(f"predictor_agent: {exc}")
        return state


═══════════════════════════════════════════════════════════
ЧАСТЬ 7: LANGGRAPH ОРКЕСТРАТОР
═══════════════════════════════════════════════════════════

## src/agents/orchestrator.py:

from langgraph.graph import StateGraph, END
from .base_agent import AgentState
from .scout_agent     import PartnershipScoutAgent
from .enricher_agent  import DataEnricherAgent
from .analyzer_agent  import CompatibilityAnalyzerAgent
from .writer_agent    import OutreachWriterAgent
from .predictor_agent import AnalyticsPredictorAgent


def should_run_enricher(state: AgentState) -> str:
    """Обогащать только если пришло событие company_created."""
    return "enricher" if state.company_id else "skip_enricher"


def should_analyze(state: AgentState) -> str:
    """Анализировать совместимость, если заданы обе компании."""
    return "analyzer" if (state.company_a_id and state.company_b_id) else "predictor"


def should_write_outreach(state: AgentState) -> str:
    """Генерировать письмо только если score > 0.7."""
    return "writer" if state.should_notify else "predictor"


def build_graph(
    scout:    PartnershipScoutAgent,
    enricher: DataEnricherAgent,
    analyzer: CompatibilityAnalyzerAgent,
    writer:   OutreachWriterAgent,
    predictor:AnalyticsPredictorAgent,
) -> "CompiledGraph":

    graph = StateGraph(AgentState)

    # ─── Регистрируем узлы ──────────────────────────────────────
    graph.add_node("scout",     scout.run)
    graph.add_node("enricher",  enricher.run)
    graph.add_node("analyzer",  analyzer.run)
    graph.add_node("writer",    writer.run)
    graph.add_node("predictor", predictor.run)

    # ─── Входная точка ──────────────────────────────────────────
    graph.set_entry_point("scout")

    # ─── Рёбра ──────────────────────────────────────────────────
    # Scout → условно enricher или skip
    graph.add_conditional_edges(
        "scout",
        should_run_enricher,
        {"enricher": "enricher", "skip_enricher": "analyzer"},
    )
    # Enricher → условно analyzer или predictor
    graph.add_conditional_edges(
        "enricher",
        should_analyze,
        {"analyzer": "analyzer", "predictor": "predictor"},
    )
    # Analyzer → условно writer или predictor
    graph.add_conditional_edges(
        "analyzer",
        should_write_outreach,
        {"writer": "writer", "predictor": "predictor"},
    )
    graph.add_edge("writer",    "predictor")
    graph.add_edge("predictor", END)

    return graph.compile()


═══════════════════════════════════════════════════════════
ЧАСТЬ 8: RAG PIPELINE
═══════════════════════════════════════════════════════════

## src/rag/retriever.py:

from rank_bm25 import BM25Okapi
from .reranker import CrossEncoderReranker
from ..embeddings.embedding_service import EmbeddingService


class HybridRetriever:
    """
    Гибридный поиск: pgvector (dense) + BM25 (sparse).
    Объединение через Reciprocal Rank Fusion (k=60).
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        db_session,
        top_k: int = 20,
    ):
        self.embedder = embedding_service
        self.db = db_session
        self.top_k = top_k

    async def retrieve(self, query: str) -> list[dict]:
        embedding = await self.embedder.embed(query)

        # Dense retrieval (pgvector)
        dense_hits = await self._vector_search(embedding)

        # Sparse retrieval (BM25 по полю ai_summary)
        sparse_hits = await self._bm25_search(query)

        # RRF fusion
        fused = self._rrf_fusion(dense_hits, sparse_hits)
        return fused[:self.top_k]

    async def _vector_search(self, embedding: list[float]) -> list[dict]:
        from sqlalchemy import text
        result = await self.db.execute(text("""
            SELECT id::text, name, ai_summary,
                   1 - (embedding <=> :emb::vector) AS score
            FROM companies
            WHERE deleted_at IS NULL AND embedding IS NOT NULL
            ORDER BY embedding <=> :emb::vector
            LIMIT 50
        """), {"emb": str(embedding)})
        return [dict(r._mapping) for r in result.fetchall()]

    async def _bm25_search(self, query: str) -> list[dict]:
        # Упрощённо: получаем тексты из БД и считаем BM25 in-memory
        # В продакшене — Elasticsearch BM25
        from sqlalchemy import text
        result = await self.db.execute(text(
            "SELECT id::text, name, ai_summary FROM companies "
            "WHERE deleted_at IS NULL AND ai_summary IS NOT NULL LIMIT 500"
        ))
        rows = [dict(r._mapping) for r in result.fetchall()]
        if not rows:
            return []

        corpus = [r["ai_summary"].lower().split() for r in rows]
        bm25 = BM25Okapi(corpus)
        scores = bm25.get_scores(query.lower().split())
        ranked = sorted(zip(rows, scores), key=lambda x: x[1], reverse=True)[:50]
        return [{"id": r["id"], "name": r["name"],
                 "ai_summary": r["ai_summary"], "score": s} for r, s in ranked]

    @staticmethod
    def _rrf_fusion(*ranked_lists, k: int = 60) -> list[dict]:
        scores: dict[str, float] = {}
        docs: dict[str, dict] = {}
        for ranked in ranked_lists:
            for rank, doc in enumerate(ranked, start=1):
                doc_id = doc["id"]
                scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
                docs[doc_id] = doc
        return [docs[did] for did in
                sorted(scores, key=lambda x: scores[x], reverse=True)]


## src/rag/reranker.py:

from sentence_transformers import CrossEncoder


RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class CrossEncoderReranker:
    """Cross-encoder для финального ранжирования топ-N документов."""

    def __init__(self):
        self._model: CrossEncoder | None = None

    def _get_model(self) -> CrossEncoder:
        if self._model is None:
            self._model = CrossEncoder(RERANKER_MODEL)
        return self._model

    def rerank(self, query: str, docs: list[dict], top_k: int = 5) -> list[dict]:
        if not docs:
            return []
        model = self._get_model()
        pairs = [(query, d.get("ai_summary", d.get("name", ""))) for d in docs]
        scores = model.predict(pairs)
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in ranked[:top_k]]


## src/rag/pipeline.py:

from .retriever import HybridRetriever
from .reranker  import CrossEncoderReranker
from ..llm.router import LLMRouter


RAG_SYSTEM = """
Ты — AI-ассистент платформы ALGORITHMIC ARTS.
Отвечай на вопросы, используя ТОЛЬКО предоставленный контекст.
Если ответа нет в контексте — скажи об этом честно.
"""


class RAGPipeline:
    """Retrieve → Rerank → Generate."""

    def __init__(
        self,
        retriever: HybridRetriever,
        reranker: CrossEncoderReranker,
        llm_router: LLMRouter,
        context_window: int = 6000,
    ):
        self.retriever = retriever
        self.reranker  = reranker
        self.llm       = llm_router
        self.max_ctx   = context_window

    async def answer(self, question: str) -> dict:
        docs = await self.retriever.retrieve(question)
        top_docs = self.reranker.rerank(question, docs, top_k=5)

        context = "\n\n".join(
            f"[{d['name']}]\n{d.get('ai_summary','')}" for d in top_docs
        )[: self.max_ctx]

        prompt = f"Контекст:\n{context}\n\nВопрос: {question}"
        response = await self.llm.generate(prompt, system=RAG_SYSTEM)
        return {"answer": response.content, "sources": [d["name"] for d in top_docs]}


═══════════════════════════════════════════════════════════
ЧАСТЬ 9: CELERY ЗАДАЧИ И KAFKA CONSUMER
═══════════════════════════════════════════════════════════

## src/tasks/celery_app.py:

from celery import Celery
from celery.schedules import crontab
from ..config import settings

celery_app = Celery(
    "ai_core",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.tasks.enrichment", "src.tasks.scouting", "src.tasks.embedding"],
)

celery_app.conf.beat_schedule = {
    "scout-partnerships": {
        "task": "src.tasks.scouting.scout_partnerships_task",
        "schedule": crontab(minute="*/15"),    # каждые 15 минут
    },
    "generate-embeddings-batch": {
        "task": "src.tasks.embedding.generate_missing_embeddings",
        "schedule": crontab(minute=0, hour="*/2"),   # каждые 2 часа
    },
}


## src/tasks/enrichment.py:

from .celery_app import celery_app
from uuid import UUID


@celery_app.task(
    name="src.tasks.enrichment.enrich_company",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def enrich_company_task(self, company_id: str) -> dict:
    """Запускает DataEnricherAgent для конкретной компании."""
    import asyncio
    from ..agents.base_agent import AgentState
    # Импортируем зависимости из DI-контейнера
    from ..container import get_enricher_agent, get_orchestrator

    state = AgentState(trigger="enrichment_requested",
                       company_id=UUID(company_id))
    result = asyncio.run(get_orchestrator().ainvoke(state))
    return {"company_id": company_id, "enriched": result.enriched_company}


## src/kafka/consumers.py:

from aiokafka import AIOKafkaConsumer
import json
import structlog

log = structlog.get_logger()


async def start_ai_consumers():
    """Слушает company.created → запускает enrich_company_task."""
    consumer = AIOKafkaConsumer(
        "company.created",
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="ai-core-service",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    await consumer.start()
    try:
        async for msg in consumer:
            event = msg.value
            company_id = event.get("company_id")
            if company_id:
                # Откладываем в Celery, не блокируем consumer
                enrich_company_task.delay(company_id)
                log.info("enrich_task_queued", company_id=company_id)
    finally:
        await consumer.stop()


═══════════════════════════════════════════════════════════
ЧАСТЬ 10: ЭНДПОИНТЫ И ПРИМЕРЫ ТЕСТОВ
═══════════════════════════════════════════════════════════

## src/routers/ai.py — HTTP эндпоинты:

Реализуй следующие эндпоинты:

POST   /ai/enrich/company           # body: {company_id}
POST   /ai/analyze/compatibility    # body: {company_a_id, company_b_id}
POST   /ai/generate/pitch           # body: {partnership_id, style}
POST   /ai/embedding/generate       # body: {text}
POST   /ai/chat                     # body: {question, session_id}
GET    /ai/models/available         # список провайдеров + статус circuit breaker
GET    /ai/prompts/{key}/stats      # статистика A/B по промпту


## Примеры тестов:

### tests/unit/test_llm_router.py:

import pytest
from unittest.mock import AsyncMock, patch
from src.llm.router import LLMRouter, AllProvidersFailedError
from src.llm.providers.base import LLMResponse, LLMUsage

def make_response(provider="mock"):
    return LLMResponse("result", provider, "model",
        LLMUsage(100, 50, 150, 0.01), 200)

@pytest.mark.asyncio
async def test_router_uses_first_available_provider():
    p1 = AsyncMock(); p1.priority=1; p1.name="p1"
    p1.is_available.return_value = True
    p1.generate = AsyncMock(return_value=make_response("p1"))
    p1.record_success = AsyncMock()
    router = LLMRouter([p1])
    resp = await router.generate("test")
    assert resp.provider == "p1"

@pytest.mark.asyncio
async def test_router_falls_back_on_error():
    p1 = AsyncMock(); p1.priority=1; p1.name="p1"
    p1.is_available.return_value = True
    p1.generate = AsyncMock(side_effect=Exception("API error"))
    p1.record_failure = AsyncMock()
    p2 = AsyncMock(); p2.priority=2; p2.name="p2"
    p2.is_available.return_value = True
    p2.generate = AsyncMock(return_value=make_response("p2"))
    p2.record_success = AsyncMock()
    router = LLMRouter([p1, p2])
    resp = await router.generate("test")
    assert resp.provider == "p2"

@pytest.mark.asyncio
async def test_router_raises_when_all_fail():
    p1 = AsyncMock(); p1.priority=1; p1.name="p1"
    p1.is_available.return_value = True
    p1.generate = AsyncMock(side_effect=Exception("fail"))
    p1.record_failure = AsyncMock()
    router = LLMRouter([p1])
    with pytest.raises(AllProvidersFailedError):
        await router.generate("test")

@pytest.mark.asyncio
async def test_circuit_breaker_skips_failed_provider():
    p1 = AsyncMock(); p1.priority=1; p1.name="p1"
    p1.is_available.return_value = False   # Circuit open
    p2 = AsyncMock(); p2.priority=2; p2.name="p2"
    p2.is_available.return_value = True
    p2.generate = AsyncMock(return_value=make_response("p2"))
    p2.record_success = AsyncMock()
    router = LLMRouter([p1, p2])
    resp = await router.generate("test")
    assert resp.provider == "p2"
    p1.generate.assert_not_called()

ОБЩИЕ ТРЕБОВАНИЯ:
- Все агенты принимают AgentState и возвращают AgentState
- LLMRouter перехватывает ALL исключения, не только HTTP
- EmbeddingService: thread-safe lazy init модели
- RAGPipeline: context_window = 6000 токенов (не символов)
- Celery: retry с exponential backoff, max_retries=3
- Prometheus: llm_calls_total{provider,status}, llm_latency_seconds, llm_cost_rub_total
- Health check проверяет: Redis, PostgreSQL, все LLM-провайдеры (health_check())

Создай полную реализацию всех компонентов.
```

---

## Промпт №6: Data Pipeline Service (Расширенный)

### Задача
Создать ETL-пайплайн для автоматического сбора и нормализации данных о российских SaaS-компаниях.

### Промпт

```markdown
Создай Data Pipeline Service для ALGORITHMIC ARTS.
Python 3.12, FastAPI, Scrapy 2.11, Celery 5.4, aiokafka 0.11,
rapidfuzz 3.x, spacy 3.7 (ru_core_news_sm).

═══════════════════════════════════════════════════════════
ЧАСТЬ 1: ФАЙЛОВАЯ СТРУКТУРА
═══════════════════════════════════════════════════════════

services/data-pipeline/
├── pyproject.toml
├── Dockerfile
└── src/
    ├── main.py
    ├── config.py
    │
    ├── scrapers/
    │   ├── __init__.py
    │   ├── base_scraper.py        # BaseScraper ABC: retry, anti-bot
    │   ├── vc_ru.py               # VCRuScraper: RSS + статьи
    │   ├── rusbase.py             # RusbaseScraper: API + web
    │   ├── habr_career.py         # HabrCareerScraper: вакансии → tech_stack
    │   ├── egrul.py               # EGRULScraper: ИНН/ОГРН → юрданные
    │   └── crunchbase.py          # CrunchbaseScraper: международные компании
    │
    ├── transform/
    │   ├── __init__.py
    │   ├── normalizer.py          # normalize_company_data()
    │   ├── ner_extractor.py       # NER: компании, суммы, технологии
    │   ├── funding_parser.py      # Парсинг "500 млн руб" → int (копейки)
    │   ├── tech_extractor.py      # Извлечение стека по тексту
    │   ├── industry_classifier.py # ML-классификация индустрии
    │   └── deduplicator.py        # rapidfuzz дедупликация
    │
    ├── load/
    │   ├── __init__.py
    │   ├── kafka_producer.py      # Публикует company.raw_data
    │   ├── db_loader.py           # Batch upsert в PostgreSQL
    │   └── es_indexer.py          # Обновляет Elasticsearch индекс
    │
    ├── tasks/
    │   ├── celery_app.py          # Celery + Beat schedule
    │   ├── scrape_tasks.py        # По одной задаче на источник
    │   └── process_tasks.py       # process_raw_company_task
    │
    ├── kafka/
    │   └── consumers.py           # company.raw_data → normalize → load
    │
    └── monitoring/
        └── metrics.py             # Prometheus счётчики


═══════════════════════════════════════════════════════════
ЧАСТЬ 2: BASE SCRAPER (anti-bot, retry)
═══════════════════════════════════════════════════════════

## src/scrapers/base_scraper.py:

import asyncio
import random
import time
import httpx
import structlog
from abc import ABC, abstractmethod

log = structlog.get_logger()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]


class ScraperError(Exception):
    pass


class BaseScraper(ABC):
    """
    Базовый класс с:
    - случайным User-Agent
    - задержками между запросами (polite crawling)
    - exponential backoff (3 попытки)
    - опциональным прокси
    """
    MIN_DELAY = 1.0    # сек между запросами
    MAX_DELAY = 3.0
    MAX_RETRIES = 3

    def __init__(self, proxy_url: str | None = None):
        self._proxy = proxy_url

    def _random_headers(self) -> dict:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    async def _get(self, url: str, **kwargs) -> httpx.Response:
        """GET с retry и exponential backoff."""
        last_exc: Exception | None = None
        for attempt in range(self.MAX_RETRIES):
            try:
                await asyncio.sleep(
                    random.uniform(self.MIN_DELAY, self.MAX_DELAY)
                )
                async with httpx.AsyncClient(
                    headers=self._random_headers(),
                    proxies=self._proxy,
                    follow_redirects=True,
                    timeout=30.0,
                ) as client:
                    resp = await client.get(url, **kwargs)
                    resp.raise_for_status()
                    return resp

            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                last_exc = exc
                wait = 2 ** attempt
                log.warning("scraper_retry",
                            url=url, attempt=attempt+1, wait=wait,
                            error=str(exc))
                await asyncio.sleep(wait)

        raise ScraperError(
            f"Не удалось загрузить {url} после {self.MAX_RETRIES} попыток: {last_exc}"
        )

    @abstractmethod
    async def scrape(self) -> list[dict]:
        """Возвращает список сырых данных компаний."""
        ...


═══════════════════════════════════════════════════════════
ЧАСТЬ 3: SCRAPERS
═══════════════════════════════════════════════════════════

## src/scrapers/vc_ru.py:

import re
from xml.etree import ElementTree as ET
from .base_scraper import BaseScraper
import structlog

log = structlog.get_logger()

VC_RSS_URL = "https://vc.ru/rss/all"
FUNDING_PATTERN = re.compile(
    r"(\d[\d\s]*(?:\.\d+)?)\s*(млн|млрд|тыс)?\s*(руб|рублей|\$|€|USD|EUR)?",
    re.IGNORECASE,
)


class VCRuScraper(BaseScraper):
    """
    Парсит RSS-фид VC.ru: находит статьи о финансировании стартапов.
    Извлекает: название компании, описание, сумма раунда, ссылка.
    """

    async def scrape(self) -> list[dict]:
        resp = await self._get(VC_RSS_URL)
        items = self._parse_rss(resp.text)
        results = []
        for item in items[:30]:  # не более 30 статей за раз
            if self._is_startup_article(item.get("title", "")):
                detail = await self._scrape_article(item["link"])
                if detail:
                    results.append({**item, **detail, "source": "vc.ru"})
        log.info("vc_ru_scraped", items_found=len(results))
        return results

    def _parse_rss(self, xml_text: str) -> list[dict]:
        root = ET.fromstring(xml_text)
        items = []
        for item in root.findall(".//item"):
            items.append({
                "title":       item.findtext("title", ""),
                "link":        item.findtext("link", ""),
                "description": item.findtext("description", ""),
                "pub_date":    item.findtext("pubDate", ""),
            })
        return items

    def _is_startup_article(self, title: str) -> bool:
        keywords = ["стартап", "раунд", "инвестиц", "привлек", "финансирован",
                    "запустил", "сервис", "платформ"]
        title_lower = title.lower()
        return any(kw in title_lower for kw in keywords)

    async def _scrape_article(self, url: str) -> dict | None:
        try:
            resp = await self._get(url)
            text = resp.text
            funding = self._extract_funding(text)
            company_name = self._extract_company_name_from_title(
                resp.headers.get("title", "")
            )
            return {
                "raw_description": text[:2000],
                "funding_text": funding,
                "company_name_hint": company_name,
                "source_url": url,
            }
        except Exception as exc:
            log.warning("vc_ru_article_failed", url=url, error=str(exc))
            return None

    def _extract_funding(self, text: str) -> str | None:
        m = FUNDING_PATTERN.search(text)
        return m.group(0) if m else None

    @staticmethod
    def _extract_company_name_from_title(title: str) -> str:
        # "Сервис X привлёк Y млн" → "X"
        parts = title.split(" ")
        return " ".join(parts[:3]) if parts else ""


## src/scrapers/habr_career.py:

from .base_scraper import BaseScraper
import structlog

log = structlog.get_logger()
HABR_API = "https://career.habr.com/api/v1/vacancies"

TECH_KEYWORDS = {
    "python": ["python", "django", "fastapi", "flask"],
    "javascript": ["javascript", "typescript", "node.js", "nodejs"],
    "react": ["react", "react.js", "reactjs"],
    "vue": ["vue", "vue.js", "vuejs", "nuxt"],
    "golang": ["golang", "go lang", " go "],
    "postgresql": ["postgresql", "postgres"],
    "redis": ["redis"],
    "kafka": ["kafka", "apache kafka"],
    "kubernetes": ["kubernetes", "k8s"],
    "docker": ["docker"],
    "elasticsearch": ["elasticsearch", "elastic"],
    "mongodb": ["mongodb", "mongo"],
}


class HabrCareerScraper(BaseScraper):
    """
    Парсит вакансии Habr Карьера для определения tech_stack компаний.
    Группирует по company_name, суммирует технологии.
    """

    async def scrape(self) -> list[dict]:
        page = 1
        companies: dict[str, dict] = {}

        while page <= 5:
            resp = await self._get(HABR_API, params={
                "page": page, "per_page": 50, "type": "all"
            })
            data = resp.json()
            vacancies = data.get("list", [])
            if not vacancies:
                break

            for vac in vacancies:
                company_name = vac.get("company", {}).get("title", "")
                if not company_name:
                    continue
                skills = [s["title"].lower() for s in vac.get("skills", [])]
                description = vac.get("description", "").lower()
                tech_stack = self._extract_tech(skills, description)

                if company_name not in companies:
                    companies[company_name] = {
                        "name": company_name,
                        "website": vac.get("company", {}).get("href", ""),
                        "tech_stack": {},
                        "vacancy_count": 0,
                        "source": "habr_career",
                    }
                companies[company_name]["vacancy_count"] += 1
                for tech in tech_stack:
                    companies[company_name]["tech_stack"][tech] = True

            page += 1

        result = list(companies.values())
        log.info("habr_career_scraped", companies_found=len(result))
        return result

    def _extract_tech(self, skills: list[str], description: str) -> list[str]:
        found = []
        for tech, keywords in TECH_KEYWORDS.items():
            if any(kw in skills or kw in description for kw in keywords):
                found.append(tech)
        return found


## src/scrapers/egrul.py — ЕГРЮЛ через API Контур.Фокус:

import httpx
from .base_scraper import BaseScraper


class EGRULScraper(BaseScraper):
    """
    Обогащает компанию данными ЕГРЮЛ через API Контур.Фокус.
    Используется on-demand при создании компании, не по расписанию.
    """

    def __init__(self, api_key: str):
        super().__init__()
        self._api_key = api_key
        self._base = "https://focus-api.kontur.ru/api3"

    async def lookup_by_inn(self, inn: str) -> dict | None:
        try:
            resp = await self._get(
                f"{self._base}/req",
                params={"inn": inn, "key": self._api_key},
            )
            data = resp.json()
            if not data:
                return None
            company = data[0]
            return {
                "inn":        company.get("inn"),
                "ogrn":       company.get("ogrn"),
                "kpp":        company.get("kpp"),
                "legal_name": company.get("shortName") or company.get("fullName"),
                "is_active":  company.get("status", {}).get("dissolved") is False,
                "source":     "egrul",
            }
        except Exception:
            return None

    async def scrape(self) -> list[dict]:
        # ЕГРЮЛ не парсится пачками — используется только lookup_by_inn()
        return []


═══════════════════════════════════════════════════════════
ЧАСТЬ 4: ТРАНСФОРМАЦИЯ — NER, НОРМАЛИЗАЦИЯ, ДЕДУПЛИКАЦИЯ
═══════════════════════════════════════════════════════════

## src/transform/ner_extractor.py:

import re
import spacy
from dataclasses import dataclass

nlp = None   # Lazy-loaded

def get_nlp():
    global nlp
    if nlp is None:
        nlp = spacy.load("ru_core_news_sm")
    return nlp


@dataclass
class ExtractionResult:
    company_names:  list[str]
    funding_amount: int | None     # в копейках
    technologies:   list[str]
    location:       str | None


FUNDING_RE = re.compile(
    r"([\d\s,.]+)\s*(тыс(?:яч)?\.?|млн|миллион|млрд|миллиард)?\s*"
    r"(руб(?:лей)?|\$|долл(?:аров)?|€|евро)?",
    re.IGNORECASE,
)

MULTIPLIERS = {
    "тыс": 1_000,
    "тысяч": 1_000,
    "млн": 1_000_000,
    "миллион": 1_000_000,
    "млрд": 1_000_000_000,
    "миллиард": 1_000_000_000,
}


class NERExtractor:
    """
    Извлекает из текста:
    - названия компаний (spaCy NER)
    - суммы финансирования
    - упомянутые технологии
    - упомянутые города
    """

    def extract(self, text: str) -> ExtractionResult:
        nlp_model = get_nlp()
        doc = nlp_model(text[:10_000])

        companies = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        locations = [ent.text for ent in doc.ents if ent.label_ == "LOC"]

        return ExtractionResult(
            company_names=list(dict.fromkeys(companies))[:5],
            funding_amount=self._extract_funding(text),
            technologies=self._extract_technologies(text),
            location=locations[0] if locations else None,
        )

    def _extract_funding(self, text: str) -> int | None:
        m = FUNDING_RE.search(text)
        if not m:
            return None
        try:
            amount_str = m.group(1).replace(" ", "").replace(",", ".")
            amount = float(amount_str)
            multiplier_key = (m.group(2) or "").lower().rstrip(".")
            multiplier = MULTIPLIERS.get(multiplier_key, 1)
            currency = (m.group(3) or "руб").lower()
            amount_rub = amount * multiplier
            if any(c in currency for c in ["$", "долл", "usd"]):
                amount_rub *= 90  # упрощённый курс, в проде — из API
            return int(amount_rub * 100)  # в копейках
        except (ValueError, OverflowError):
            return None

    def _extract_technologies(self, text: str) -> list[str]:
        from .tech_extractor import TechExtractor
        return TechExtractor().extract(text)


## src/transform/normalizer.py:

import re
from .ner_extractor  import NERExtractor
from .funding_parser import parse_funding_amount
from .tech_extractor import TechExtractor
from .industry_classifier import IndustryClassifier
from pydantic import BaseModel, field_validator


class RawCompanyData(BaseModel):
    name:          str | None = None
    description:   str | None = None
    website:       str | None = None
    funding_text:  str | None = None
    location:      str | None = None
    tech_stack:    dict = {}
    source:        str = "unknown"
    source_url:    str | None = None

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, v):
        if not v:
            return v
        v = re.sub(r"\s+", " ", v).strip()
        v = re.sub(r'["""«»]', "", v)
        return v[:255]


class NormalizedCompany(BaseModel):
    name:                 str
    description:          str | None
    website:              str | None
    industry:             str
    tech_stack:           dict
    funding_total:        int | None    # в копейках
    headquarters_city:    str | None
    source_url:           str | None
    source:               str


ner       = NERExtractor()
tech_ext  = TechExtractor()
ind_cls   = IndustryClassifier()


def normalize_company_data(raw: dict) -> NormalizedCompany | None:
    try:
        data = RawCompanyData(**raw)

        name = data.name
        description = data.description or ""

        # 1. Если нет имени, пробуем NER
        if not name:
            ner_result = ner.extract(description)
            if ner_result.company_names:
                name = ner_result.company_names[0]
            else:
                return None  # невозможно идентифицировать компанию

        # 2. Финансирование
        funding = (
            parse_funding_amount(data.funding_text)
            if data.funding_text
            else None
        )

        # 3. Tech stack — объединяем из источника и NER
        tech = {**data.tech_stack, **dict.fromkeys(tech_ext.extract(description), True)}

        # 4. Индустрия
        industry = ind_cls.classify(description or name)

        # 5. Город
        city = data.location
        if not city and description:
            ner_result = ner.extract(description)
            city = ner_result.location

        return NormalizedCompany(
            name=name,
            description=description[:2000] if description else None,
            website=data.website,
            industry=industry,
            tech_stack=tech,
            funding_total=funding,
            headquarters_city=city,
            source_url=data.source_url,
            source=data.source,
        )
    except Exception:
        return None


## src/transform/deduplicator.py — rapidfuzz вместо fuzzywuzzy:

from rapidfuzz import fuzz, process
from rapidfuzz.distance import Indel
import unicodedata
import re


def _normalize_name(name: str) -> str:
    """Нормализуем название: нижний регистр, убираем ООО/ЗАО/ИП, пробелы."""
    name = unicodedata.normalize("NFC", name.lower())
    name = re.sub(r"\b(ооо|зао|пао|ао|ип|нпо|нко)\b", "", name)
    name = re.sub(r'["""«»"\',.()\-]', " ", name)
    return re.sub(r"\s+", " ", name).strip()


class Deduplicator:
    """
    Находит дубли компаний через rapidfuzz.
    Порог: 88 (token_set_ratio) — оптимально для русских названий.
    """

    THRESHOLD = 88

    async def find_duplicate(
        self, new_name: str, existing_names: list[tuple[str, str]]
    ) -> str | None:
        """
        existing_names: [(company_id, company_name), ...]
        Возвращает company_id дубликата или None.
        """
        if not existing_names:
            return None

        norm_new = _normalize_name(new_name)
        candidates = {cid: _normalize_name(cname) for cid, cname in existing_names}

        # Быстрый фильтр: берём топ-10 кандидатов по prefix
        top_10 = process.extract(
            norm_new,
            candidates,
            scorer=fuzz.token_set_ratio,
            limit=10,
        )

        for cid, score, _ in top_10:
            if score >= self.THRESHOLD:
                return cid

        return None

    @staticmethod
    def is_duplicate(name_a: str, name_b: str) -> bool:
        """Быстрая проверка двух конкретных имён."""
        a = _normalize_name(name_a)
        b = _normalize_name(name_b)
        return fuzz.token_set_ratio(a, b) >= 88


## src/transform/tech_extractor.py:

import re

TECH_PATTERNS: dict[str, list[str]] = {
    "python":       [r"\bpython\b", r"\bdjango\b", r"\bfastapi\b", r"\bflask\b"],
    "javascript":   [r"\bjavascript\b", r"\btypescript\b", r"\bnodejs?\b"],
    "react":        [r"\breact\.?js\b", r"\breactjs\b"],
    "vue":          [r"\bvue\.?js\b", r"\bnuxt\b"],
    "golang":       [r"\bgolang\b", r"\bgo lang\b"],
    "java":         [r"\bjava\b(?!script)", r"\bspring boot\b", r"\bkotlin\b"],
    "postgresql":   [r"\bpostgresql\b", r"\bpostgres\b"],
    "mysql":        [r"\bmysql\b", r"\bmariadb\b"],
    "mongodb":      [r"\bmongodb\b", r"\bmongo\b"],
    "redis":        [r"\bredis\b"],
    "kafka":        [r"\bkafka\b"],
    "kubernetes":   [r"\bkubernetes\b", r"\bk8s\b"],
    "docker":       [r"\bdocker\b"],
    "elasticsearch":[r"\belasticsearch\b", r"\belastic\b"],
    "clickhouse":   [r"\bclickhouse\b"],
    "1c":           [r"\b1с\b", r"\b1c\b", r"\bbitrix\b"],
}


class TechExtractor:
    def extract(self, text: str) -> list[str]:
        text_lower = text.lower()
        found = []
        for tech, patterns in TECH_PATTERNS.items():
            if any(re.search(p, text_lower) for p in patterns):
                found.append(tech)
        return found


## src/transform/industry_classifier.py:

INDUSTRY_KEYWORDS: dict[str, list[str]] = {
    "Fintech":      ["банк", "финтех", "платёж", "кредит", "инвестиц", "payment", "banking"],
    "Edtech":       ["образован", "обучен", "курс", "школ", "edtech", "learning"],
    "Healthtech":   ["медицин", "здоровь", "клиник", "телемедицин", "health"],
    "Martech":      ["маркетинг", "реклам", "crm", "лидоген", "marketing"],
    "HRtech":       ["hr", "кадр", "подбор", "рекрутин", "вакансий"],
    "Logtech":      ["логистик", "доставк", "склад", "транспорт"],
    "Cybersecurity":["безопасность", "security", "кибер", "защит"],
    "Proptech":     ["недвижим", "аренд", "ипотек", "proptech"],
    "SaaS":         ["saas", "подписк", "b2b", "автоматизац", "платформ"],
    "Ecommerce":    ["интернет-магазин", "маркетплейс", "ecommerce", "торговл"],
}


class IndustryClassifier:
    """Простой keyword-based классификатор. В продакшне — ML модель."""

    def classify(self, text: str) -> str:
        text_lower = text.lower()
        scores: dict[str, int] = {}
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score:
                scores[industry] = score
        if scores:
            return max(scores, key=lambda k: scores[k])
        return "SaaS"  # Дефолт для платформы


═══════════════════════════════════════════════════════════
ЧАСТЬ 5: CELERY ЗАДАЧИ И РАСПИСАНИЕ
═══════════════════════════════════════════════════════════

## src/tasks/celery_app.py:

from celery import Celery
from celery.schedules import crontab
from ..config import settings

celery_app = Celery(
    "data_pipeline",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "src.tasks.scrape_tasks",
        "src.tasks.process_tasks",
    ],
)

celery_app.conf.beat_schedule = {
    "scrape-vc-ru": {
        "task": "src.tasks.scrape_tasks.scrape_vc_ru",
        "schedule": crontab(minute=0),               # каждый час
    },
    "scrape-rusbase": {
        "task": "src.tasks.scrape_tasks.scrape_rusbase",
        "schedule": crontab(minute=30, hour="*/2"),  # каждые 2 часа
    },
    "scrape-habr-career": {
        "task": "src.tasks.scrape_tasks.scrape_habr_career",
        "schedule": crontab(hour=6, minute=0),       # ежедневно в 6:00
    },
    "scrape-crunchbase": {
        "task": "src.tasks.scrape_tasks.scrape_crunchbase",
        "schedule": crontab(hour=2, minute=0, day_of_week=1),  # еженедельно пн
    },
}

celery_app.conf.task_serializer = "json"
celery_app.conf.result_expires = 3600
celery_app.conf.worker_prefetch_multiplier = 1  # один task за раз
celery_app.conf.task_acks_late = True  # ACK после выполнения, не до


## src/tasks/scrape_tasks.py:

from .celery_app import celery_app
from ..monitoring.metrics import (
    scraper_runs, scraper_items, scraper_errors
)


@celery_app.task(
    name="src.tasks.scrape_tasks.scrape_vc_ru",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def scrape_vc_ru(self) -> dict:
    import asyncio
    from ..scrapers.vc_ru import VCRuScraper
    from ..load.kafka_producer import publish_raw_companies

    scraper_runs.labels(source="vc_ru").inc()
    try:
        items = asyncio.run(VCRuScraper().scrape())
        asyncio.run(publish_raw_companies(items))
        scraper_items.labels(source="vc_ru").inc(len(items))
        return {"source": "vc_ru", "items": len(items)}
    except Exception as exc:
        scraper_errors.labels(source="vc_ru").inc()
        raise


@celery_app.task(
    name="src.tasks.scrape_tasks.scrape_habr_career",
    bind=True, max_retries=3, default_retry_delay=600,
    autoretry_for=(Exception,), retry_backoff=True,
)
def scrape_habr_career(self) -> dict:
    import asyncio
    from ..scrapers.habr_career import HabrCareerScraper
    from ..load.kafka_producer import publish_raw_companies

    scraper_runs.labels(source="habr_career").inc()
    items = asyncio.run(HabrCareerScraper().scrape())
    asyncio.run(publish_raw_companies(items))
    scraper_items.labels(source="habr_career").inc(len(items))
    return {"source": "habr_career", "items": len(items)}


## src/tasks/process_tasks.py:

@celery_app.task(
    name="src.tasks.process_tasks.process_raw_company",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def process_raw_company_task(self, raw_data: dict) -> dict:
    """Нормализация → дедупликация → upsert в БД."""
    import asyncio
    from ..transform.normalizer  import normalize_company_data
    from ..transform.deduplicator import Deduplicator
    from ..load.db_loader        import upsert_company

    normalized = normalize_company_data(raw_data)
    if not normalized:
        return {"status": "skipped", "reason": "normalization_failed"}

    result = asyncio.run(upsert_company(normalized))
    return {"status": "ok", "company_id": str(result)}


═══════════════════════════════════════════════════════════
ЧАСТЬ 6: KAFKA CONSUMER + LOAD
═══════════════════════════════════════════════════════════

## src/kafka/consumers.py:

from aiokafka import AIOKafkaConsumer
import json, structlog

log = structlog.get_logger()


async def start_raw_data_consumer():
    """
    Слушает company.raw_data →
    запускает process_raw_company_task в Celery.
    """
    consumer = AIOKafkaConsumer(
        "company.raw_data",
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="data-pipeline-processor",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        max_poll_records=50,
    )
    await consumer.start()
    log.info("raw_data_consumer_started")
    try:
        async for msg in consumer:
            raw = msg.value
            from .tasks.process_tasks import process_raw_company_task
            process_raw_company_task.delay(raw)
    finally:
        await consumer.stop()


## src/load/kafka_producer.py:

from aiokafka import AIOKafkaProducer
import json, structlog

log = structlog.get_logger()


async def publish_raw_companies(items: list[dict]) -> None:
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
    )
    await producer.start()
    try:
        for item in items:
            await producer.send("company.raw_data", value=item)
        await producer.flush()
        log.info("raw_companies_published", count=len(items))
    finally:
        await producer.stop()


## src/load/db_loader.py:

from sqlalchemy.dialects.postgresql import insert as pg_insert
from uuid import uuid4
import re


def _slugify(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r"[^a-zа-я0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug[:200]


async def upsert_company(normalized, session) -> str:
    """
    Upsert по slug (уникальный ключ).
    Если компания уже есть — обновляем только непустые поля.
    """
    stmt = pg_insert(CompanyORM).values(
        id=uuid4(),
        name=normalized.name,
        slug=_slugify(normalized.name),
        description=normalized.description,
        website=normalized.website,
        industry=normalized.industry,
        tech_stack=normalized.tech_stack,
        funding_total=normalized.funding_total,
        headquarters_city=normalized.headquarters_city,
        source_url=normalized.source_url,
    ).on_conflict_do_update(
        index_elements=["slug"],
        set_={
            "description":       stmt.excluded.description,
            "tech_stack":        stmt.excluded.tech_stack,
            "funding_total":     stmt.excluded.funding_total,
            "headquarters_city": stmt.excluded.headquarters_city,
            "updated_at":        sa.func.now(),
        },
        where=stmt.excluded.description.isnot(None),
    ).returning(CompanyORM.id)

    result = await session.execute(stmt)
    await session.commit()
    return str(result.scalar_one())


═══════════════════════════════════════════════════════════
ЧАСТЬ 7: МОНИТОРИНГ + ПРИМЕРЫ ТЕСТОВ
═══════════════════════════════════════════════════════════

## src/monitoring/metrics.py:

from prometheus_client import Counter, Histogram, Gauge

scraper_runs  = Counter("scraper_runs_total",
    "Число запусков scrapers", ["source"])
scraper_items = Counter("scraper_items_total",
    "Число собранных элементов", ["source"])
scraper_errors= Counter("scraper_errors_total",
    "Ошибки scrapers", ["source"])
pipeline_latency = Histogram("pipeline_processing_seconds",
    "Время обработки одной записи")
duplicate_rate   = Gauge("duplicate_rate",
    "Доля дубликатов в последнем батче")
companies_per_day = Gauge("companies_added_per_day",
    "Новых компаний за последние 24ч")


## tests/unit/test_normalizer.py:

import pytest
from src.transform.normalizer import normalize_company_data, RawCompanyData
from src.transform.deduplicator import Deduplicator


class TestNormalizer:

    def test_extracts_name_from_description_via_ner(self):
        raw = {
            "name": None,
            "description": "Компания Яндекс запустила новый SaaS сервис",
            "source": "vc.ru",
        }
        result = normalize_company_data(raw)
        assert result is not None
        assert "Яндекс" in result.name

    def test_parses_funding_in_kopecks(self):
        raw = {
            "name": "TestCo",
            "description": "Компания привлекла 50 млн рублей инвестиций",
            "funding_text": "50 млн рублей",
            "source": "vc.ru",
        }
        result = normalize_company_data(raw)
        assert result is not None
        assert result.funding_total == 50_000_000 * 100  # 50 млн в копейках

    def test_returns_none_for_empty_data(self):
        result = normalize_company_data({"name": None, "description": None})
        assert result is None

    def test_extracts_tech_stack(self):
        raw = {
            "name": "DevCo",
            "description": "Используем Python FastAPI и PostgreSQL для backend",
            "source": "habr",
        }
        result = normalize_company_data(raw)
        assert result is not None
        assert "python" in result.tech_stack
        assert "postgresql" in result.tech_stack


class TestDeduplicator:

    @pytest.mark.asyncio
    async def test_finds_duplicate_with_llc_prefix(self):
        dedup = Deduplicator()
        existing = [("id-1", "ООО Яндекс"), ("id-2", "ЗАО Сбербанк")]
        dup_id = await dedup.find_duplicate("Яндекс", existing)
        assert dup_id == "id-1"

    @pytest.mark.asyncio
    async def test_no_duplicate_for_different_companies(self):
        dedup = Deduplicator()
        existing = [("id-1", "Тинькофф Банк"), ("id-2", "ВТБ")]
        dup_id = await dedup.find_duplicate("1С-Битрикс", existing)
        assert dup_id is None

    def test_is_duplicate_fuzzy(self):
        assert Deduplicator.is_duplicate("Яндекс.Маркет", "Яндекс Маркет")
        assert not Deduplicator.is_duplicate("Яндекс", "Сбербанк")


## tests/unit/test_ner_extractor.py:

class TestNERExtractor:

    def test_extracts_funding_millions(self):
        from src.transform.ner_extractor import NERExtractor
        ext = NERExtractor()
        result = ext._extract_funding("Стартап привлёк 150 млн руб инвестиций")
        assert result == 150_000_000 * 100  # в копейках

    def test_extracts_funding_billions(self):
        from src.transform.ner_extractor import NERExtractor
        ext = NERExtractor()
        result = ext._extract_funding("Раунд составил 2 млрд рублей")
        assert result == 2_000_000_000 * 100

    def test_returns_none_when_no_funding(self):
        from src.transform.ner_extractor import NERExtractor
        ext = NERExtractor()
        result = ext._extract_funding("Компания запустила новый продукт")
        assert result is None


ОБЩИЕ ТРЕБОВАНИЯ:
- BaseScraper: все GET через _get() — никаких прямых httpx вызовов
- Delays между запросами: random.uniform(1.0, 3.0) сек
- Kafka: company.raw_data → consume → process_raw_company_task.delay()
- Celery: task_acks_late=True, worker_prefetch_multiplier=1
- Все scraper-задачи: autoretry_for=(Exception,), retry_backoff=True
- upsert через ON CONFLICT (slug) DO UPDATE
- Prometheus: scraper_runs_total, scraper_items_total, scraper_errors_total
- Health check проверяет: БД, Redis, Kafka

Создай полную реализацию всех scrapers, transform-слоя и Celery-задач.
```

---

## Чеклист улучшений относительно исходных промптов

### Промпт №5 — что добавлено:
- Полная файловая структура с аннотацией каждого файла
- Реализация всех 3 LLM-провайдеров (YandexGPT, GigaChat, OpenRouter) с OAuth2 для GigaChat
- `LLMUsage` dataclass с отслеживанием стоимости в рублях
- `LLMRouter` с Circuit Breaker (3 ошибки → 60 сек пауза) и exponential backoff
- Prometheus метрики: `llm_calls_total`, `llm_latency_seconds`, `llm_cost_rub_total`
- `PromptManager`: версионирование промптов в Redis, A/B-тест по весам
- `EmbeddingService`: Redis-кэш по SHA-256, batch с `mget`/pipeline
- `AgentState` dataclass — единое состояние для всех агентов
- Все 5 агентов с system prompts, форматом ответа JSON и обработкой ошибок
- 3 стиля outreach-письма с отдельными шаблонами (formal/friendly/technical)
- `LangGraph` граф с conditional edges и `set_entry_point`
- `HybridRetriever`: pgvector + BM25 + RRF fusion
- `CrossEncoderReranker` (ms-marco-MiniLM-L-6-v2)
- `RAGPipeline`: retrieve → rerank → generate, context_window=6000
- Celery Beat расписание (scout каждые 15 мин, embeddings каждые 2 ч)
- 4 unit-теста LLMRouter (fallback, circuit breaker, AllProvidersFailedError)

### Промпт №6 — что добавлено:
- Полная файловая структура (scrapers/transform/load/tasks/kafka/monitoring)
- `BaseScraper` ABC: User-Agent ротация (4 агента), случайные задержки, exponential backoff
- `VCRuScraper`: RSS-парсинг через ElementTree, regex для суммы финансирования
- `HabrCareerScraper`: API вакансий, group by company, keyword-based tech detection
- `EGRULScraper`: API Контур.Фокус by INN, on-demand (не по расписанию)
- `NERExtractor` (spaCy ru_core_news_sm): ORG, LOC, суммы с мультипликаторами
- `TechExtractor`: regex-паттерны для 15 технологий
- `IndustryClassifier`: keyword scoring, 10 категорий
- `Deduplicator` (rapidfuzz): `token_set_ratio >= 88`, нормализация ООО/ЗАО
- `normalize_company_data()`: полный pipeline из 5 шагов
- Celery Beat: 4 задачи с правильным расписанием + `task_acks_late=True`
- `upsert_company()` через `ON CONFLICT (slug) DO UPDATE`
- Kafka producer (`publish_raw_companies`) + consumer (`process_raw_company_task`)
- Prometheus: `scraper_runs_total`, `scraper_items_total`, `scraper_errors_total`
- 7 unit-тестов (normalizer: 4, deduplicator: 3, NER: 3)
