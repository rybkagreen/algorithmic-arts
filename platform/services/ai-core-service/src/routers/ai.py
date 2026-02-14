from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from .config import settings
from .llm.router import LLMRouter
from .agents.analyzer_agent import CompatibilityAnalyzerAgent
from .agents.writer_agent import OutreachWriterAgent
from .llm.providers.yandexgpt import YandexGPTProvider
from .llm.providers.gigachat import GigaChatProvider
from .llm.providers.openrouter import OpenRouterProvider
from .agents.base_agent import AgentState
from .tasks.enrichment import enrich_company_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

router = APIRouter(prefix="/ai", tags=["AI"])

# Инициализация зависимостей
engine = create_async_engine(settings.POSTGRES_DSN)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

llm_providers = [
    YandexGPTProvider(api_key=settings.YANDEX_API_KEY, folder_id=settings.YANDEX_FOLDER_ID),
    GigaChatProvider(api_key=settings.GIGACHAT_API_KEY),
    OpenRouterProvider(api_key=settings.OPENROUTER_API_KEY),
]
llm_router = LLMRouter(llm_providers)

# Создаем граф агентов
scout_agent = None  # будет инициализирован в lifespan
analyzer_agent = None
writer_agent = None
enricher_agent = None
predictor_agent = None
ai_graph = None

class GenerateRequest(BaseModel):
    prompt: str
    system: str = ""
    provider: str | None = None

class AnalyzePartnershipRequest(BaseModel):
    company_a_id: UUID
    company_b_id: UUID
    outreach_style: str = "formal"

@router.post("/generate")
async def generate(request: GenerateRequest):
    """Генерация текста через LLM Router."""
    try:
        response = await llm_router.generate(
            prompt=request.prompt,
            system=request.system,
            required_provider=request.provider
        )
        return {
            "content": response.content,
            "provider": response.provider,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "cost_rub": response.usage.cost_rub,
            },
            "latency_ms": response.latency_ms,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-partnership")
async def analyze_partnership(request: AnalyzePartnershipRequest):
    """Анализ совместимости двух компаний."""
    try:
        state = AgentState(
            trigger="user_request",
            company_a_id=request.company_a_id,
            company_b_id=request.company_b_id,
            outreach_style=request.outreach_style,
        )
        
        # Запускаем анализ через агенты
        async with async_session() as session:
            analyzer = CompatibilityAnalyzerAgent(llm_router, session)
            writer = OutreachWriterAgent(llm_router)
            
            state = await analyzer.run(state)
            if state.compatibility_report:
                state = await writer.run(state)
        
        return {
            "compatibility_score": state.compatibility_score,
            "report": state.compatibility_report,
            "outreach_message": state.outreach_message,
            "should_notify": state.should_notify,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enrich-company/{company_id}")
async def enrich_company(company_id: UUID):
    """Запускает обогащение компании через Celery."""
    try:
        enrich_company_task.delay(str(company_id))
        return {"status": "enrichment_scheduled", "company_id": str(company_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))