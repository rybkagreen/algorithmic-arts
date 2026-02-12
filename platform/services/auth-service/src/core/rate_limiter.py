"""Rate limiter for auth service."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from shared.logging import get_logger

logger = get_logger("rate-limiter")

# Create rate limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri="redis://redis:6379/1",
    headers_enabled=True,
    retry_after_headers=True,
    strategy="fixed-window",
    in_memory_fallback=True,
)

# Custom rate limit decorator
def rate_limit(limit: str):
    """Decorator for rate limiting endpoints."""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator