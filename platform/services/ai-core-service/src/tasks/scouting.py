from celery_app import celery_app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from agents.scout_agent import PartnershipScoutAgent
from llm.router import LLMRouter
from llm.providers.yandexgpt import YandexGPTProvider
from llm.providers.gigachat import GigaChatProvider
from llm.providers.openrouter import OpenRouterProvider
import httpx

# Инициализация зависимостей
engine = create_async_engine("postgresql+asyncpg://ai_core:password@postgres:5432/ai_core")
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

llm_providers = [
    YandexGPTProvider(api_key="YOUR_YANDEX_API_KEY", folder_id="YOUR_FOLDER_ID"),
    GigaChatProvider(api_key="YOUR_GIGACHAT_API_KEY"),
    OpenRouterProvider(api_key="YOUR_OPENROUTER_API_KEY"),
]
llm_router = LLMRouter(llm_providers)
scout_agent = PartnershipScoutAgent(llm_router, httpx.AsyncClient())

@celery_app.task(name="ai_core.scout_partnerships")
def scout_partnerships_task() -> dict:
    """Запускает PartnershipScoutAgent для поиска партнёрств."""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def run_scout():
            state = {"trigger": "scheduled"}
            result_state = await scout_agent.run(state)
            return {
                "status": "success",
                "found_companies": len(result_state.scout_insights),
                "errors": result_state.errors,
            }
        
        result = loop.run_until_complete(run_scout())
        return result
    except Exception as exc:
        return {"status": "error", "error": str(exc)}