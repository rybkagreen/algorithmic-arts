import httpx
import time
import structlog
from .base import BaseLLMProvider, LLMResponse, LLMUsage

log = structlog.get_logger()

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

        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            resp = await client.post(
                "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                json={
                    "model": self._model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                },
                headers={"Authorization": f"Bearer {token}"},
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
        return LLMResponse(
            content=content,
            provider=self.name,
            model=self._model,
            usage=usage,
            latency_ms=int((time.time() - start) * 1000),
        )

    async def health_check(self) -> bool:
        try:
            resp = await self.generate("ping")
            return "ping" in resp.content.lower() or "pong" in resp.content.lower()
        except Exception:
            return False