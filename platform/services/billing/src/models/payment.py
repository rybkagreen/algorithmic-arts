import uuid

from sqlalchemy import Column, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import BaseModel, TimestampMixin


class Payment(BaseModel, TimestampMixin):
    __tablename__ = "payments"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(PGUUID(as_uuid=True), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="RUB")
    status = Column(String(50), nullable=False)
    payment_method = Column(String(50))
    external_payment_id = Column(String(255))
    paid_at = Column(DateTime(timezone=True))