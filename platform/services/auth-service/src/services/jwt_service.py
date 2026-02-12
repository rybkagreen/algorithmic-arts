import time
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from jose import JWTError, jwt
from redis.asyncio import Redis

from .config import settings
from .core.exceptions import InvalidTokenError


class JWTService:
    """
    RS256 JWT с ротацией ключей и Redis-blacklist.
    Access token: 15 минут
    Refresh token: 30 дней
    """

    ACCESS_TOKEN_TTL = 900          # 15 минут
    REFRESH_TOKEN_TTL = 2592000     # 30 дней
    ALGORITHM = "RS256"

    def __init__(self, redis: Redis):
        self.redis = redis
        self._private_key = settings.jwt.private_key
        self._public_key = settings.jwt.public_key

    async def create_access_token(self, user_id: UUID, role: str) -> str:
        jti = str(uuid4())
        now = int(time.time())
        payload = {
            "sub": str(user_id),
            "role": role,
            "type": "access",
            "iat": now,
            "exp": now + self.ACCESS_TOKEN_TTL,
            "jti": jti,
        }
        return jwt.encode(payload, self._private_key, algorithm=self.ALGORITHM)

    async def create_refresh_token(self, user_id: UUID) -> str:
        jti = str(uuid4())
        now = int(time.time())
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": now,
            "exp": now + self.REFRESH_TOKEN_TTL,
            "jti": jti,
        }
        token = jwt.encode(payload, self._private_key, algorithm=self.ALGORITHM)
        # Сохраняем JTI в Redis для последующего отзыва
        await self.redis.setex(
            f"refresh_token:{user_id}:{jti}",
            self.REFRESH_TOKEN_TTL,
            "valid"
        )
        return token

    async def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self._public_key, algorithms=[self.ALGORITHM])
        except JWTError as e:
            raise InvalidTokenError(f"Токен недействителен: {e}")

        # Проверяем blacklist
        jti = payload.get("jti")
        if jti and await self.redis.exists(f"blacklist:{jti}"):
            raise InvalidTokenError("Токен отозван")

        return payload

    async def revoke_token(self, token: str) -> None:
        """Добавляет JTI в blacklist."""
        try:
            payload = jwt.decode(
                token, self._public_key, algorithms=[self.ALGORITHM],
                options={"verify_exp": False}
            )
            jti = payload.get("jti")
            exp = payload.get("exp", 0)
            ttl = max(0, exp - int(time.time()))
            if jti and ttl > 0:
                await self.redis.setex(f"blacklist:{jti}", ttl, "revoked")
        except JWTError:
            pass  # Уже невалидный токен — игнорируем