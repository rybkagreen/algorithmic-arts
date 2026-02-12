import json
from .base_scraper import BaseScraper
import structlog

log = structlog.get_logger()

FOCUS_API_BASE_URL = "https://focus-api.kontur.ru/api3"

class EGRULScraper(BaseScraper):
    """
    Парсит данные из Контур.Фокус API.
    Вызывается только on-demand при создании компании по ИНН/ОГРН.
    Возвращает пустой список в scrape() — так как это не регулярный скрапинг.
    """

    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key

    async def scrape(self) -> list[dict]:
        # EGRULScraper вызывается только on-demand, не через регулярный скрапинг
        # Поэтому возвращаем пустой список для Celery Beat
        return []

    async def get_company_by_inn(self, inn: str) -> dict | None:
        """Получает данные компании по ИНН."""
        try:
            url = f"{FOCUS_API_BASE_URL}/req"
            params = {"inn": inn, "key": self.api_key}
            resp = await self._get(url, params=params)
            data = resp.json()
            
            if not data.get("items"):
                return None
                
            company = data["items"][0]
            
            return {
                "inn": company.get("inn"),
                "ogrn": company.get("ogrn"),
                "kpp": company.get("kpp"),
                "legal_name": company.get("shortName") or company.get("fullName"),
                "legal_address": company.get("address", {}).get("parsedAddressRF", {}).get("fullAddress"),
                "reg_date": company.get("registrationDate"),
                "is_active": not company.get("status", {}).get("dissolved", False),
                "okved_main": company.get("okved"),
                "source": "egrul",
            }
        except Exception as exc:
            log.warning("egrul_api_failed", inn=inn, error=str(exc))
            return None

    async def get_company_by_ogrn(self, ogrn: str) -> dict | None:
        """Получает данные компании по ОГРН."""
        try:
            url = f"{FOCUS_API_BASE_URL}/req"
            params = {"ogrn": ogrn, "key": self.api_key}
            resp = await self._get(url, params=params)
            data = resp.json()
            
            if not data.get("items"):
                return None
                
            company = data["items"][0]
            
            return {
                "inn": company.get("inn"),
                "ogrn": company.get("ogrn"),
                "kpp": company.get("kpp"),
                "legal_name": company.get("shortName") or company.get("fullName"),
                "legal_address": company.get("address", {}).get("parsedAddressRF", {}).get("fullAddress"),
                "reg_date": company.get("registrationDate"),
                "is_active": not company.get("status", {}).get("dissolved", False),
                "okved_main": company.get("okved"),
                "source": "egrul",
            }
        except Exception as exc:
            log.warning("egrul_api_failed", ogrn=ogrn, error=str(exc))
            return None