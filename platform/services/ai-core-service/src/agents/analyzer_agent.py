import json
import structlog
from .base_agent import AgentState
from ..llm.router import LLMRouter
from ..tools.company_tools import get_company

log = structlog.get_logger()

ANALYZER_SYSTEM_PROMPT = """
Ты — эксперт по B2B SaaS партнёрствам. Дай развёрнутый анализ совместимости двух компаний.
Результат верни СТРОГО в JSON:
{
  "score": 0.82,
  "strengths": ["общая аудитория", "дополняющий функционал"],
  "risks": ["конкуренция в CRM-сегменте"],
  "recommended_type": "integration",
  "pitch_angle": "Предложите интеграцию через API для автоматизации онбординга"
}
"""


class CompatibilityAnalyzerAgent:
    def __init__(self, llm_router: LLMRouter, company_service_client):
        self.llm = llm_router
        self.company_client = company_service_client

    async def run(self, state: AgentState) -> AgentState:
        if not (state.company_a_id and state.company_b_id):
            return state
            
        try:
            company_a = await get_company(state.company_a_id, self.company_client)
            company_b = await get_company(state.company_b_id, self.company_client)
            
            if not company_a or not company_b:
                state.errors.append("analyzer_agent: company not found")
                return state
                
            prompt = (
                f"Компания A: {company_a}\n\n"
                f"Компания B: {company_b}\n\n"
                f"Оцени совместимость и дай рекомендации."
            )
            response = await self.llm.generate(prompt, system=ANALYZER_SYSTEM_PROMPT)
            report = json.loads(response.content)
            
            state.compatibility_score = report.get("score")
            state.compatibility_report = report
            state.should_notify = (state.compatibility_score or 0) > 0.7
            
        except Exception as exc:
            error_msg = f"analyzer_agent: {exc}"
            state.errors.append(error_msg)
            log.error("analyzer_agent_error", error=error_msg, traceback=str(exc))
        return state