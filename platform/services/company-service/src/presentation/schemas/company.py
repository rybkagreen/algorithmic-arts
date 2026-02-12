from typing import List, Optional

from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: str
    sub_industries: List[str] = Field(default_factory=list)
    business_model: Optional[str] = None
    founded_year: Optional[int] = None
    headquarters_country: str
    headquarters_city: Optional[str] = None
    employees_count: Optional[int] = None
    employees_range: Optional[str] = None
    funding_total_amount: Optional[float] = None
    funding_total_currency: Optional[str] = "USD"
    funding_stage: Optional[str] = None
    last_funding_date: Optional[str] = None
    inn_value: Optional[str] = None
    ogrn_value: Optional[str] = None
    legal_name: Optional[str] = None
    tech_stack: dict = Field(default_factory=dict)
    integrations: List[str] = Field(default_factory=list)
    api_available: bool = False
    is_verified: bool = False


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    sub_industries: Optional[List[str]] = None
    business_model: Optional[str] = None
    founded_year: Optional[int] = None
    headquarters_country: Optional[str] = None
    headquarters_city: Optional[str] = None
    employees_count: Optional[int] = None
    employees_range: Optional[str] = None
    funding_total_amount: Optional[float] = None
    funding_total_currency: Optional[str] = None
    funding_stage: Optional[str] = None
    last_funding_date: Optional[str] = None
    inn_value: Optional[str] = None
    ogrn_value: Optional[str] = None
    legal_name: Optional[str] = None
    tech_stack: Optional[dict] = None
    integrations: Optional[List[str]] = None
    api_available: Optional[bool] = None
    is_verified: Optional[bool] = None