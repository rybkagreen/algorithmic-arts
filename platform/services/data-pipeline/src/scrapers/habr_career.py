from .base_scraper import BaseScraper
import structlog

log = structlog.get_logger()

HABR_API_URL = "https://career.habr.com/api/v1/vacancies"
TECH_KEYWORDS = {
    "python": ["python", "django", "fastapi", "flask"],
    "javascript": ["javascript", "typescript", "node.js", "nodejs"],
    "react": ["react", "react.js", "reactjs"],
    "vue": ["vue", "vue.js", "vuejs", "nuxt"],
    "golang": ["golang", "go lang", " go "],
    "postgresql": ["postgresql", "postgres"],
    "redis": ["redis"],
    "kafka": ["kafka", "apache kafka"],
    "kubernetes": ["kubernetes", "k8s"],
    "docker": ["docker"],
    "elasticsearch": ["elasticsearch", "elastic"],
    "mongodb": ["mongodb", "mongo"],
}


class HabrCareerScraper(BaseScraper):
    """
    Парсит вакансии Habr Career.
    Группирует по company.title, извлекает tech_stack из skills + description.
    """

    async def scrape(self) -> list[dict]:
        try:
            # Получаем первые 50 вакансий (максимум за один запрос)
            resp = await self._get(HABR_API_URL, params={"limit": "50"})
            data = resp.json()
            
            # Группируем вакансии по компаниям
            companies_dict = {}
            
            for vac in data.get("vacancies", []):
                company_data = vac.get("company", {})
                company_name = company_data.get("title", "").strip()
                if not company_name:
                    continue
                    
                # Создаем или получаем существующую компанию
                if company_name not in companies_dict:
                    companies_dict[company_name] = {
                        "name": company_name,
                        "website": company_data.get("href"),
                        "vacancy_count": 0,
                        "tech_stack": {},
                        "employees_hint": company_data.get("size"),
                        "source": "habr_career",
                        "source_url": f"https://career.habr.com/companies/{company_data.get('slug', '')}",
                    }
                
                # Инкрементируем счетчик вакансий
                companies_dict[company_name]["vacancy_count"] += 1
                
                # Извлекаем технологии из skills (приоритет)
                skills = vac.get("skills", [])
                for skill in skills:
                    skill_lower = skill.lower()
                    for tech, keywords in TECH_KEYWORDS.items():
                        if any(kw in skill_lower for kw in keywords):
                            companies_dict[company_name]["tech_stack"][tech] = True
                            break
                
                # Дополнительно из description
                description = vac.get("description", "")
                for tech, keywords in TECH_KEYWORDS.items():
                    if any(kw in description.lower() for kw in keywords):
                        companies_dict[company_name]["tech_stack"][tech] = True
            
            # Преобразуем dict в list
            results = list(companies_dict.values())
            log.info("habr_career_scraped", companies_found=len(results))
            return results
            
        except Exception as exc:
            log.warning("habr_career_failed", error=str(exc))
            return []