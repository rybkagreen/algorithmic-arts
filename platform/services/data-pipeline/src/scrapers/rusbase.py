import re
import json
from .base_scraper import BaseScraper
import structlog

log = structlog.get_logger()

RUSBASE_API_URL = "https://rusbase.com/api/v1/news"
RUSBASE_WEB_URL = "https://rusbase.com"

FUNDING_PATTERN = re.compile(
    r"(\d[\d\s]*(?:\.\d+)?)\s*(млн|млрд|тыс)?\s*(руб|рублей|\$|€|USD|EUR)?",
    re.IGNORECASE,
)


class RusbaseScraper(BaseScraper):
    """
    Парсит API и веб-страницы Rusbase.
    Извлекает статьи о финансировании, новых компаниях, партнёрствах.
    """

    async def scrape(self) -> list[dict]:
        # Сначала API (быстрее)
        api_results = await self._scrape_api()
        # Затем веб (если нужно больше данных)
        web_results = await self._scrape_web()
        
        results = api_results + web_results[:20]  # максимум 20 из веба
        log.info("rusbase_scraped", api_items=len(api_results), web_items=len(web_results))
        return results

    async def _scrape_api(self) -> list[dict]:
        try:
            resp = await self._get(RUSBASE_API_URL, params={"limit": "50"})
            data = resp.json()
            items = []
            for item in data.get("items", [])[:30]:
                if self._is_relevant_news(item.get("title", "")):
                    items.append({
                        "title": item.get("title", ""),
                        "link": f"{RUSBASE_WEB_URL}{item.get('url', '')}",
                        "description": item.get("excerpt", ""),
                        "pub_date": item.get("published_at", ""),
                        "source": "rusbase",
                    })
            return items
        except Exception as exc:
            log.warning("rusbase_api_failed", error=str(exc))
            return []

    async def _scrape_web(self) -> list[dict]:
        try:
            # Получаем главную страницу и парсим последние новости
            resp = await self._get(RUSBASE_WEB_URL)
            # Упрощённо: ищем ссылки на новости в HTML
            # В реальном коде использовался бы BeautifulSoup или lxml
            # Здесь имитируем парсинг через регулярки
            import re
            pattern = r'<a href="(/news/[^"]+)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, resp.text)
            
            items = []
            for url, title in matches[:20]:
                if self._is_relevant_news(title):
                    items.append({
                        "title": title,
                        "link": f"{RUSBASE_WEB_URL}{url}",
                        "description": "",
                        "pub_date": "",
                        "source": "rusbase",
                    })
            return items
        except Exception as exc:
            log.warning("rusbase_web_failed", error=str(exc))
            return []

    def _is_relevant_news(self, title: str) -> bool:
        keywords = ["стартап", "инвестиц", "раунд", "финансирован", "новая компания",
                    "партнёрство", "сервис", "платформа"]
        title_lower = title.lower()
        return any(kw in title_lower for kw in keywords)

    async def _scrape_article(self, url: str) -> dict | None:
        try:
            resp = await self._get(url)
            text = resp.text
            funding = self._extract_funding(text)
            company_name = self._extract_company_name(text)
            return {
                "raw_description": text[:2000],
                "funding_text": funding,
                "company_name_hint": company_name,
                "source_url": url,
            }
        except Exception as exc:
            log.warning("rusbase_article_failed", url=url, error=str(exc))
            return None

    def _extract_funding(self, text: str) -> str | None:
        m = FUNDING_PATTERN.search(text)
        return m.group(0) if m else None

    @staticmethod
    def _extract_company_name(text: str) -> str:
        # Простой подход: ищем первое имя компании после "компания" или "стартап"
        words = text.lower().split()
        for i, word in enumerate(words):
            if word in ["компания", "стартап", "сервис"]:
                if i + 1 < len(words):
                    return words[i + 1].capitalize()
        return ""