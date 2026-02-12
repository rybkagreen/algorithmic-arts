import json
from uuid import UUID

from redis.asyncio import Redis


class UserCacheService:
    """Read-through кэш для профилей пользователей. TTL = 1 час."""

    TTL = 3600
    KEY_PREFIX = "user_profile:"

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, user_id: UUID) -> dict | None:
        data = await self.redis.get(f"{self.KEY_PREFIX}{user_id}")
        return json.loads(data) if data else None

    async def set(self, user_id: UUID, profile: dict) -> None:
        await self.redis.setex(
            f"{self.KEY_PREFIX}{user_id}",
            self.TTL,
            json.dumps(profile, default=str)
        )

    async def invalidate(self, user_id: UUID) -> None:
        await self.redis.delete(f"{self.KEY_PREFIX}{user_id}")