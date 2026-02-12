"""Shared Pydantic schemas for all services."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Base schema with common fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str = "healthy"
    service: str
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationResponse(BaseModel):
    """Pagination response schema."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    message: str
    code: int
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EventMetadata(BaseModel):
    """Event metadata schema."""
    event_id: UUID = Field(default_factory=UUID)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    source_service: str
    correlation_id: Optional[str] = None


class CompanyReference(BaseModel):
    """Company reference schema."""
    id: UUID
    name: str
    slug: str


class UserReference(BaseModel):
    """User reference schema."""
    id: UUID
    email: str
    full_name: str
    role: str


class MetricValue(BaseModel):
    """Metric value schema."""
    value: float
    unit: str
    period_start: datetime
    period_end: datetime


class SearchQuery(BaseModel):
    """Search query schema."""
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10
    offset: int = 0
    sort_by: Optional[str] = None
    sort_order: str = "asc"


class CompatibilityScore(BaseModel):
    """Compatibility score schema."""
    score: float = Field(ge=0.0, le=1.0)
    factors: Dict[str, float]
    explanation: str