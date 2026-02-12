import json
from .base_scraper import BaseScraper
import structlog

log = structlog.get_logger()

CRUNCHBASE_API_BASE_URL = "https://api.crunchbase.com/api/v4"
CRUNCHBASE_SEARCH_ENDPOINT = "/searches/organizations"

# Маппинг для employee_count
EMPLOYEE_COUNT_MAPPING = {
    "c_00001_00010": "1-10",
    "c_00011_00050": "11-50",
    "c_00051_00100": "51-200",
    "c_00101_00250": "51-200",
    "c_00251_00500": "201-500",
    "c_00501_001000": "500+",
}

# Маппинг для funding_type
FUNDING_TYPE_MAPPING = {
    "seed": "seed", "angel": "pre_seed",
    "series_a": "series_a", "series_b": "series_b",
    "series_c": "series_c", "ipo": "ipo",
    "bootstrapped": "bootstrapped",
}


class CrunchbaseScraper(BaseScraper):
    """
    Парсит данные из Crunchbase Basic API.
    Ищет компании в России, возвращает 25 компаний за запрос.
    """

    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key

    async def scrape(self) -> list[dict]:
        try:
            # Поиск компаний в России
            url = f"{CRUNCHBASE_API_BASE_URL}{CRUNCHBASE_SEARCH_ENDPOINT}"
            headers = {"X-CB-USER-API-KEY": self.api_key}
            
            payload = {
                "field_ids": [
                    "identifier", "short_description", "website_url",
                    "categories", "founded_on", "employee_count",
                    "funding_total", "last_funding_type", "last_funding_at",
                    "location_identifiers", "rank_org"
                ],
                "query": [
                    {
                        "type": "predicate",
                        "field_id": "facet_ids",
                        "operator_id": "includes",
                        "values": ["company"]
                    },
                    {
                        "type": "predicate",
                        "field_id": "location_identifiers",
                        "operator_id": "includes",
                        "values": ["Russia"]
                    }
                ],
                "order": [{"field_id": "rank_org", "sort": "asc"}],
                "limit": 25
            }
            
            resp = await self._get(url, json=payload, headers=headers)
            data = resp.json()
            
            results = []
            for org in data.get("entities", []):
                properties = org.get("properties", {})
                
                # Извлекаем основные поля
                name = properties.get("identifier", {}).get("value", "")
                description = properties.get("short_description")
                website = properties.get("website_url")
                categories = properties.get("categories", [])
                founded_on = properties.get("founded_on", {}).get("value", "")[:4] if properties.get("founded_on") else ""
                employee_count_raw = properties.get("employee_count")
                funding_total_usd = properties.get("funding_total", {}).get("value_usd")
                last_funding_type = properties.get("last_funding_type")
                location_identifiers = properties.get("location_identifiers", [])
                
                # Маппинг полей
                industry = categories[0] if categories else "SaaS"
                employees_range = self._map_employee_count(employee_count_raw)
                funding_stage = self._map_funding_type(last_funding_type)
                
                # Конвертируем funding_total в копейки (USD → RUB × 100)
                funding_total_kopeks = None
                if funding_total_usd:
                    funding_total_kopeks = int(funding_total_usd * 90 * 100)  # USD → RUB × 100
                
                result = {
                    "name": name,
                    "description": description,
                    "website": website,
                    "industry": industry,
                    "founded_year": founded_on,
                    "employees_range": employees_range,
                    "funding_total": funding_total_kopeks,
                    "funding_stage": funding_stage,
                    "headquarters_country": "RU",
                    "source": "crunchbase",
                }
                results.append(result)
            
            log.info("crunchbase_scraped", companies_found=len(results))
            return results
            
        except Exception as exc:
            log.warning("crunchbase_api_failed", error=str(exc))
            return []

    @staticmethod
    def _map_employee_count(cb_range: str) -> str:
        return EMPLOYEE_COUNT_MAPPING.get(cb_range, "1-10")

    @staticmethod
    def _map_funding_type(cb_type: str) -> str:
        return FUNDING_TYPE_MAPPING.get(cb_type, "unknown")