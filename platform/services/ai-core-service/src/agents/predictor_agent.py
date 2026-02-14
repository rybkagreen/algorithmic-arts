import json
import structlog
from .base_agent import AgentState
from ..llm.router import LLMRouter
from ..tools.company_tools import get_company

log = structlog.get_logger()

PREDICTOR_SYSTEM_PROMPT = """
Ты — аналитик по B2B партнёрствам. Прогнозируй вероятность заключения сделки.
Результат верни СТРОГО в JSON:
{
  "deal_probability": 0.85,
  "confidence": "high",
  "key_factors": ["сильная совместимость", "рыночный спрос"],
  "risk_factors": ["конкуренция", "географическая дистанция"]
}
"""


class AnalyticsPredictorAgent:
    def __init__(self, llm_router: LLMRouter, company_service_client):
        self.llm = llm_router
        self.company_client = company_service_client

    async def run(self, state: AgentState) -> AgentState:
        if not (state.company_a_id and state.company_b_id and state.compatibility_report):
            return state
            
        try:
            company_a = await get_company(state.company_a_id, self.company_client)
            company_b = await get_company(state.company_b_id, self.company_client)
            
            if not company_a or not company_b:
                state.errors.append("predictor_agent: company not found")
                return state
                
            prompt = (
                f"Компания A: {company_a}\n\n"
                f"Компания B: {company_b}\n\n"
                f"Совместимость: {state.compatibility_report}\n\n"
                f"Прогнозируй вероятность сделки и факторы риска."
            )
            response = await self.llm.generate(prompt, system=PREDICTOR_SYSTEM_PROMPT)
            prediction = json.loads(response.content)
            
            state.deal_probability = prediction.get("deal_probability")
            
        except Exception as exc:
            error_msg = f"predictor_agent: {exc}"
            state.errors.append(error_msg)
            log.error("predictor_agent_error", error=error_msg, traceback=str(exc))
        return state