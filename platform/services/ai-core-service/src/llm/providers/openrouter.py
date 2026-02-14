import httpx
import time
import structlog
from .base import BaseLLMProvider, LLMResponse, LLMUsage

log = structlog.get_logger()

OPENROUTER_COST_PER_1K = 0.003  # USD → ~0.27 руб (примерно)

class OpenRouterProvider(BaseLLMProvider):
    name = "openrouter"
    priority = 3  # fallback последний

    # Используй эти модели в порядке приоритета:
    DEFAULT_MODEL = "anthropic/claude-sonnet-4-5"
    FALLBACK_MODEL = "openai/gpt-4o"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        self._api_key = api_key
        self._model = model
        self._base_url = "https://openrouter.ai/api/v1"

    async def generate(self, prompt: str, system: str = "") -> LLMResponse:
        start = time.time()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self._base_url}/chat/completions",
                json={
                    "model": self._model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                },
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "HTTP-Referer": "https://algorithmic-arts.ru",
                    "X-Title": "ALGORITHMIC ARTS",
                },
            )
            resp.raise_for_status()

        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        usage_raw = data.get("usage", {})
        # OpenRouter возвращает стоимость в USD
        cost_usd: float = data.get("usage", {}).get("cost", 0) or 0
        cost_rub: float = cost_usd * 90  # курс

        return LLMResponse(
            content=content,
            provider=self.name,
            model=self._model,
            usage=LLMUsage(
                prompt_tokens=usage_raw.get("prompt_tokens", 0),
                completion_tokens=usage_raw.get("completion_tokens", 0),
                total_tokens=usage_raw.get("total_tokens", 0),
                cost_rub=cost_rub,
            ),
            latency_ms=int((time.time() - start) * 1000),
        )

    async def health_check(self) -> bool:
        try:
            resp = await self.generate("ping")
            return "ping" in resp.content.lower() or "pong" in resp.content.lower()
        except Exception:
            return False