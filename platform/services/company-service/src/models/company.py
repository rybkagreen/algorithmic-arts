import uuid

from sqlalchemy import (
    ARRAY,
    JSON,
    Boolean,
    Column,
    Date,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.dialects.postgresql import VECTOR

from .base import BaseModel, TimestampMixin
from .company_metric import CompanyMetric
from .company_update import CompanyUpdate


class Company(BaseModel, TimestampMixin):
    __tablename__ = "companies"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    website = Column(String(1024))
    logo_url = Column(String(2048))
    industry = Column(String(100))
    sub_industries = Column(ARRAY(String(100)))
    business_model = Column(Text)
    founded_year = Column(Integer)
    headquarters_country = Column(String(100))
    headquarters_city = Column(String(100))
    employees_count = Column(Integer)
    employees_range = Column(String(50))
    funding_total = Column(Numeric(15, 2))
    funding_stage = Column(String(50))
    last_funding_date = Column(Date)
    inn = Column(String(12))
    ogrn = Column(String(13))
    kpp = Column(String(9))
    legal_name = Column(String(255))
    tech_stack = Column(JSON)
    integrations = Column(ARRAY(String(100)))
    api_available = Column(Boolean, default=False)
    ai_summary = Column(Text)
    ai_tags = Column(ARRAY(String(50)))
    embedding = Column(VECTOR(1536))
    is_verified = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)