
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import BaseModel


class UserRole(BaseModel):
    __tablename__ = "user_roles"

    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    role_id = Column(PGUUID(as_uuid=True), nullable=False)

    __mapper_args__ = {
        "primary_key": [user_id, role_id]
    }