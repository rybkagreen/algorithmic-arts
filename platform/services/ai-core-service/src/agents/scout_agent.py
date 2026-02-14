import json
import structlog
from .base_agent import AgentState
from ..llm.router import LLMRouter

log = structlog.get_logger()

SCOUT_SYSTEM_PROMPT = """
Ты — Partnership Scout агент платформы ALGORITHMIC ARTS.
Твоя задача: анализировать новости российского B2B SaaS рынка,
выявлять новые компании и потенциальные партнёрства.

Результат верни СТРОГО в JSON:
{
  "found_companies": [{"name": "...", "industry": "...", "website": "..."}],
  "partnership_signals": [{"company_a": "...", "company_b": "...", "reason": "..."}],
  "market_trends": ["..."]
}
"""


class PartnershipScoutAgent:
    """Мониторит VC.ru, Habr Карьера, Rusbase каждые 15 минут."""

    def __init__(self, llm_router: LLMRouter, http_client):
        self.llm = llm_router
        self.http = http_client

    async def run(self, state: AgentState) -> AgentState:
        try:
            news_text = await self._fetch_news()
            response = await self.llm.generate(
                prompt=f"Проанализируй новости и найди партнёрства:\n\n{news_text[:6000]}",
                system=SCOUT_SYSTEM_PROMPT,
            )
            insights = json.loads(response.content)
            state.scout_insights = insights.get("found_companies", [])
            state.last_updated = state.last_updated
        except Exception as exc:
            error_msg = f"scout_agent: {exc}"
            state.errors.append(error_msg)
            log.error("scout_agent_error", error=error_msg, traceback=str(exc))
        return state

    async def _fetch_news(self) -> str:
        """Агрегирует RSS-фиды VC.ru, Habr, Rusbase."""
        sources = [
            "https://vc.ru/rss/all",
            "https://habr.com/ru/rss/hubs/ru_java/news/",
            "https://rusbase.com/feed/",
        ]
        texts = []
        for url in sources:
            try:
                resp = await self.http.get(url, timeout=10)
                texts.append(resp.text[:3000])
            except Exception as e:
                log.warning("rss_fetch_failed", url=url, error=str(e))
                continue
        return "\n---\n".join(texts)