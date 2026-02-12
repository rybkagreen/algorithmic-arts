from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID


@dataclass
class CompanyCreated:
    company_id: UUID
    name: str
    industry: str
    occurred_at: datetime


@dataclass
class CompanyUpdated:
    company_id: UUID
    changed_fields: List[str]
    occurred_at: datetime


@dataclass
class CompanyEnriched:
    company_id: UUID
    ai_summary: str
    ai_tags: List[str]
    occurred_at: datetime


@dataclass
class CompanyUpdateRecorded:
    company_id: UUID
    update_type: str
    changed_fields: List[str]
    occurred_at: datetime


@dataclass
class CompanyMetricRecorded:
    company_id: UUID
    metric_type: str
    value: float
    unit: str
    occurred_at: datetime