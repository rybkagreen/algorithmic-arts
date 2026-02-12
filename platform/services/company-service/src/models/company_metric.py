import uuid

from sqlalchemy import Column, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import BaseModel, TimestampMixin


class CompanyMetric(BaseModel, TimestampMixin):
    __tablename__ = "company_metrics"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Numeric(15, 2), nullable=False)
    measured_at = Column(DateTime(timezone=True), nullable=False)