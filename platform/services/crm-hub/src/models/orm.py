import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


from typing import Optional
from sqlalchemy import UUID as SQLAlchemyUUID  # noqa: E402
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CRMConnectionORM(Base):
    __tablename__ = "crm_connections"

    id: SQLAlchemyUUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: SQLAlchemyUUID = Column(UUID(as_uuid=True), nullable=False)
    crm_type: str = Column(String(20), nullable=False)  # amocrm, bitrix24, etc.
    access_token: str = Column(Text, nullable=False)  # зашифрованный токен
    refresh_token: Optional[str] = Column(Text)  # зашифрованный токен
    expires_at: Optional[datetime] = Column(DateTime(timezone=True))
    account_subdomain: Optional[str] = Column(String(100))
    account_id: Optional[str] = Column(String(100))
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at: datetime = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    is_active: bool = Column(Boolean, default=True)


class SyncLogORM(Base):
    __tablename__ = "sync_logs"

    id: SQLAlchemyUUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id: SQLAlchemyUUID = Column(
        UUID(as_uuid=True), ForeignKey("crm_connections.id"), nullable=False
    )
    sync_type: str = Column(String(20), nullable=False)  # to_crm, from_crm
    external_id: Optional[str] = Column(String(100))  # ID в CRM
    internal_id: Optional[str] = Column(String(100))  # ID во внутренней системе
    status: str = Column(String(20), nullable=False)  # success, failure
    error_message: Optional[str] = Column(Text)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    connection = relationship("CRMConnectionORM", back_populates="sync_logs")


# Добавляем обратную связь к CRMConnectionORM
CRMConnectionORM.sync_logs = relationship("SyncLogORM", back_populates="connection")
