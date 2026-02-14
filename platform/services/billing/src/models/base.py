from typing import Any

from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

Base = declarative_base()


class TimestampMixin:
    @declared_attr
    def created_at(cls) -> Column:
        return Column(DateTime(timezone=True), default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls) -> Column:
        return Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)


class BaseModel(Base):
    __abstract__ = True

    id: Any