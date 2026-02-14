from celery_app import celery_app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from agents.enricher_agent import DataEnricherAgent
from llm.router import LLMRouter
from llm.providers.yandexgpt import YandexGPTProvider
from llm.providers.gigachat import GigaChatProvider
from llm.providers.openrouter import OpenRouterProvider

# Инициализация зависимостей
engine = create_async_engine("postgresql+asyncpg://ai_core:password@postgres:5432/ai_core")
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

llm_providers = [
    YandexGPTProvider(api_key="YOUR_YANDEX_API_KEY", folder_id="YOUR_FOLDER_ID"),
    GigaChatProvider(api_key="YOUR_GIGACHAT_API_KEY"),
    OpenRouterProvider(api_key="YOUR_OPENROUTER_API_KEY"),
]
llm_router = LLMRouter(llm_providers)
enricher_agent = DataEnricherAgent(llm_router, async_session)


@celery_app.task(
    name="ai_core.enrich_company",
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
)
def enrich_company_task(self, company_id: str) -> dict:
    """Запускает DataEnricherAgent для обогащения компании."""
    try:
        # Запускаем асинхронную задачу через asyncio.run()
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def run_enrich():
            async with async_session():
                state = {
                    "company_id": company_id,
                    "trigger": "scheduled",
                }
                result_state = await enricher_agent.run(state)
                return {
                    "status": "success",
                    "company_id": company_id,
                    "enriched": bool(result_state.enriched_company),
                    "errors": result_state.errors,
                }
        
        result = loop.run_until_complete(run_enrich())
        return result
    except Exception as exc:
        raise self.retry(exc=exc)