import json
import structlog
from .base_agent import AgentState
from ..llm.router import LLMRouter
from ..tools.company_tools import get_company
from ..tools.web_tools import fetch_url
from ..tools.db_tools import update_company_enrichment

log = structlog.get_logger()

ENRICHER_SYSTEM_PROMPT = """
Ты — агент обогащения данных для платформы ALGORITHMIC ARTS.
Твоя задача: проанализировать компанию и добавить AI-генерированные метаданные.

Результат верни СТРОГО в JSON:
{
  "ai_summary": "Краткое описание компании (1–2 предложения)",
  "ai_tags": ["тег1", "тег2", "тег3"],
  "market_position": "лидер/новичок/специалист",
  "growth_potential": "высокий/средний/низкий"
}
"""


class DataEnricherAgent:
    def __init__(self, llm_router: LLMRouter, company_service_client):
        self.llm = llm_router
        self.company_client = company_service_client

    async def run(self, state: AgentState) -> AgentState:
        if not state.company_id:
            return state
            
        try:
            company = await get_company(state.company_id, self.company_client)
            if not company:
                state.errors.append("enricher_agent: company not found")
                return state
                
            # Получаем дополнительные данные с сайта
            website = company.get("website")
            extra_info = ""
            if website and website.startswith("http"):
                try:
                    html = await fetch_url(website, timeout=10)
                    extra_info = f"Сайт: {html[:500]}..."
                except Exception as e:
                    log.warning("website_fetch_failed", url=website, error=str(e))
            
            prompt = (
                f"Компания: {company}\n\n"
                f"Дополнительно: {extra_info}\n\n"
                f"Проанализируй и добавь AI-метаданные."
            )
            response = await self.llm.generate(prompt, system=ENRICHER_SYSTEM_PROMPT)
            enrichment = json.loads(response.content)
            
            # Сохраняем в БД
            await update_company_enrichment(state.company_id, enrichment, self.company_client)
            state.enriched_company = enrichment
            
        except Exception as exc:
            error_msg = f"enricher_agent: {exc}"
            state.errors.append(error_msg)
            log.error("enricher_agent_error", error=error_msg, traceback=str(exc))
        return state