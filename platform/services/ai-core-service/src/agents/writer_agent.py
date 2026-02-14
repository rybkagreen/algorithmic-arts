import structlog
from .base_agent import AgentState
from ..llm.router import LLMRouter

log = structlog.get_logger()

WRITER_PROMPTS = {
    "formal": """
Напиши официальное деловое письмо от {sender_company} к {target_company}.
Цель: предложить стратегическое партнёрство.
Аргументы: {match_reasons}
Письмо должно быть 200–300 слов, без лишних формальностей.
Верни только текст письма.
""",
    "friendly": """
Напиши дружелюбное письмо от {sender_company} к {target_company}.
Цель: предложить партнёрство.
Аргументы: {match_reasons}
Тон: неформальный, тёплый, живой. 150–200 слов.
Верни только текст письма.
""",
    "technical": """
Напиши техническое письмо от {sender_company} к {target_company}.
Цель: предложить технологическую интеграцию.
Синергия: {match_reasons}
Акцент на конкретных технических деталях. 250–350 слов.
Верни только текст письма.
""",
}


class OutreachWriterAgent:
    def __init__(self, llm_router: LLMRouter):
        self.llm = llm_router

    async def run(self, state: AgentState) -> AgentState:
        if not state.compatibility_report:
            return state
            
        try:
            template = WRITER_PROMPTS.get(state.outreach_style, WRITER_PROMPTS["formal"])
            match_reasons = ", ".join(
                state.compatibility_report.get("strengths", [])
            )
            prompt = template.format(
                sender_company="Ваша компания",
                target_company="Компания-партнёр",
                match_reasons=match_reasons,
            )
            response = await self.llm.generate(prompt)
            state.outreach_message = response.content
            
        except Exception as exc:
            error_msg = f"writer_agent: {exc}"
            state.errors.append(error_msg)
            log.error("writer_agent_error", error=error_msg, traceback=str(exc))
        return state