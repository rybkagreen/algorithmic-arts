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