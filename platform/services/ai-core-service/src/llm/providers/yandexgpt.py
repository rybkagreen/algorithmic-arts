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

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self._base_url}/completion",
                json={
                    "modelUri": f"gpt://{self._folder_id}/{self._model}",
                    "completionOptions": {
                        "stream": False,
                        "temperature": self.temperature,
                        "maxTokens": self.max_tokens,
                    },
                    "messages": messages,
                },
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