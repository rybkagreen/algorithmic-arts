"""AI schemas for AI core service."""

from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class AnalysisStyle(str, Enum):
    """Analysis style."""
    formal = "formal"
    friendly = "friendly"
    technical = "technical"


class Language(str, Enum):
    """Language."""
    russian = "russian"
    english = "english"


class CompanyBase(BaseModel):
    """Base company schema."""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    founded_year: Optional[int] = None
    headquarters_country: Optional[str] = None
    employees_count: Optional[int] = None
    tech_stack: Optional[List[str]] = None
    ai_tags: Optional[List[str]] = None
    embedding: Optional[List[float]] = None
    is_verified: bool = False
    view_count: int = 0


class CompatibilityAnalysisRequest(BaseModel):
    """Compatibility analysis request."""
    company_1: CompanyBase
    company_2: CompanyBase
    include_detailed_factors: bool = True
    analysis_style: AnalysisStyle = AnalysisStyle.technical
    language: Language = Language.russian


class CompatibilityAnalysisResponse(BaseModel):
    """Compatibility analysis response."""
    company_1: CompanyBase
    company_2: CompanyBase
    compatibility_score: float = Field(ge=0.0, le=1.0)
    factors: Dict[str, float]
    explanation: str
    created_at: str


class OutreachMessageRequest(BaseModel):
    """Outreach message request."""
    company_1: CompanyBase
    company_2: CompanyBase
    recipient_name: str
    recipient_email: str
    compatibility_score: float = Field(ge=0.0, le=1.0)
    style: AnalysisStyle = AnalysisStyle.formal
    language: Language = Language.russian
    additional_context: Optional[str] = None


class OutreachMessageResponse(BaseModel):
    """Outreach message response."""
    message: str
    style: AnalysisStyle
    language: Language
    created_at: str