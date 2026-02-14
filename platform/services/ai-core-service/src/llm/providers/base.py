from abc import ABC, abstractmethod
from dataclasses import dataclass
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