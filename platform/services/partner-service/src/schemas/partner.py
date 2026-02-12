"""Partner schemas for partner service."""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class PartnershipStatus(str, Enum):
    """Partnership status."""
    proposed = "proposed"
    accepted = "accepted"
    rejected = "rejected"
    active = "active"
    terminated = "terminated"


class CompanyBase(BaseModel):
    """Base company schema."""
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
    compatibility_score: Optional[float] = None


class CompanyCreate(CompanyBase):
    """Company creation schema."""
    pass


class CompanyUpdate(BaseModel):
    """Company update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    founded_year: Optional[int] = None
    headquarters_country: Optional[str] = None
    employees_count: Optional[int] = None
    tech_stack: Optional[List[str]] = None
    ai_tags: Optional[List[str]] = None


class CompanyOut(CompanyBase):
    """Company output schema."""
    id: str
    created_at: str
    updated_at: str
    embedding: Optional[List[float]] = None
    is_verified: bool = False
    view_count: int = 0


class PartnershipBase(BaseModel):
    """Base partnership schema."""
    company_id_1: str
    company_id_2: str
    status: PartnershipStatus = PartnershipStatus.proposed
    compatibility_score: float = 0.0
    reason: Optional[str] = None


class PartnershipCreate(PartnershipBase):
    """Partnership creation schema."""
    pass


class PartnershipUpdate(BaseModel):
    """Partnership update schema."""
    status: Optional[PartnershipStatus] = None
    compatibility_score: Optional[float] = None
    reason: Optional[str] = None


class PartnershipOut(PartnershipBase):
    """Partnership output schema."""
    id: str
    created_at: str
    updated_at: str
    company_1: CompanyOut
    company_2: CompanyOut