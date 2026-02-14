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