from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID, uuid4

from .events import CompanyCreated, CompanyEnriched, CompanyUpdated
from .exceptions import CompanyValidationError
from .value_objects import INN, OGRN, FundingAmount


@dataclass
class Company:
    """Aggregate Root для компании."""

    id: UUID
    name: str
    slug: str
    description: str | None
    website: str | None
    industry: str
    sub_industries: List[str]
    business_model: str | None
    founded_year: int | None
    headquarters_country: str
    headquarters_city: str | None
    employees_count: int | None
    employees_range: str | None
    funding_total: FundingAmount | None
    funding_stage: str | None
    last_funding_date: datetime | None
    inn: INN | None
    ogrn: OGRN | None
    legal_name: str | None
    tech_stack: dict[str, Any]
    integrations: List[str]
    api_available: bool
    ai_summary: str | None
    ai_tags: List[str]
    embedding: List[float] | None
    is_verified: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    _domain_events: List = field(default_factory=list, init=False, repr=False)

    @classmethod
    def create(cls, **kwargs) -> "Company":
        company = cls(id=uuid4(), **kwargs)
        company._domain_events.append(
            CompanyCreated(
                company_id=company.id,
                name=company.name,
                industry=company.industry,
                occurred_at=datetime.utcnow()
            )
        )
        return company

    def update(self, **kwargs) -> None:
        changed_fields = {}
        for key, value in kwargs.items():
            if hasattr(self, key) and getattr(self, key) != value:
                setattr(self, key, value)
                changed_fields[key] = value

        if changed_fields:
            self.updated_at = datetime.utcnow()
            self._domain_events.append(
                CompanyUpdated(
                    company_id=self.id,
                    changed_fields=list(changed_fields.keys()),
                    occurred_at=datetime.utcnow()
                )
            )

    def enrich(self, ai_summary: str, ai_tags: List[str], embedding: List[float]) -> None:
        self.ai_summary = ai_summary
        self.ai_tags = ai_tags
        self.embedding = embedding
        self.updated_at = datetime.utcnow()
        self._domain_events.append(
            CompanyEnriched(
                company_id=self.id,
                ai_summary=ai_summary,
                ai_tags=ai_tags,
                occurred_at=datetime.utcnow()
            )
        )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "website": self.website,
            "industry": self.industry,
            "sub_industries": self.sub_industries,
            "business_model": self.business_model,
            "founded_year": self.founded_year,
            "headquarters_country": self.headquarters_country,
            "headquarters_city": self.headquarters_city,
            "employees_count": self.employees_count,
            "employees_range": self.employees_range,
            "funding_total": self.funding_total.to_dict() if self.funding_total else None,
            "funding_stage": self.funding_stage,
            "last_funding_date": self.last_funding_date.isoformat() if self.last_funding_date else None,
            "inn": self.inn.to_dict() if self.inn else None,
            "ogrn": self.ogrn.to_dict() if self.ogrn else None,
            "legal_name": self.legal_name,
            "tech_stack": self.tech_stack,
            "integrations": self.integrations,
            "api_available": self.api_available,
            "ai_summary": self.ai_summary,
            "ai_tags": self.ai_tags,
            "embedding": self.embedding,
            "is_verified": self.is_verified,
            "view_count": self.view_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }