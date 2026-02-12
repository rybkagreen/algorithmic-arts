import re
import xml.etree.ElementTree as ET
from .base_scraper import BaseScraper
import structlog

log = structlog.get_logger()

VC_RSS_URL = "https://vc.ru/rss/all"
FUNDING_PATTERN = re.compile(
    r"(\d[\d\s]*(?:\.\d+)?)\s*(млн|млрд|тыс)?\s*(руб|рублей|\$|€|USD|EUR)?",
    re.IGNORECASE,
)


class VCRuScraper(BaseScraper):
    """
    Парсит RSS-фид VC.ru: находит статьи о финансировании стартапов.
    Извлекает: название компании, описание, сумма раунда, ссылка.
    """

    async def scrape(self) -> list[dict]:
        resp = await self._get(VC_RSS_URL)
        items = self._parse_rss(resp.text)
        results = []
        for item in items[:30]:  # не более 30 статей за раз
            if self._is_startup_article(item.get("title", "")):
                detail = await self._scrape_article(item["link"])
                if detail:
                    results.append({**item, **detail, "source": "vc.ru"})
        log.info("vc_ru_scraped", items_found=len(results))
        return results

    def _parse_rss(self, xml_text: str) -> list[dict]:
        root = ET.fromstring(xml_text)
        items = []
        for item in root.findall(".//item"):
            items.append({
                "title":       item.findtext("title", ""),
                "link":        item.findtext("link", ""),
                "description": item.findtext("description", ""),
                "pub_date":    item.findtext("pubDate", ""),
            })
        return items

    def _is_startup_article(self, title: str) -> bool:
        keywords = ["стартап", "раунд", "инвестиц", "привлек", "финансирован",
                    "запустил", "сервис", "платформ"]
        title_lower = title.lower()
        return any(kw in title_lower for kw in keywords)

    async def _scrape_article(self, url: str) -> dict | None:
        try:
            resp = await self._get(url)
            text = resp.text
            funding = self._extract_funding(text)
            company_name = self._extract_company_name_from_title(
                resp.headers.get("title", "")
            )
            return {
                "raw_description": text[:2000],
                "funding_text": funding,
                "company_name_hint": company_name,
                "source_url": url,
            }
        except Exception as exc:
            log.warning("vc_ru_article_failed", url=url, error=str(exc))
            return None

    def _extract_funding(self, text: str) -> str | None:
        m = FUNDING_PATTERN.search(text)
        return m.group(0) if m else None

    @staticmethod
    def _extract_company_name_from_title(title: str) -> str:
        # "Сервис X привлёк Y млн" → "X"
        parts = title.split(" ")
        return " ".join(parts[:3]) if parts else ""