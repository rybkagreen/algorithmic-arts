import asyncio
import random
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