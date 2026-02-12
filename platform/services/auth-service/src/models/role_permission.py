import uuid

from sqlalchemy import UUID, Column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import BaseModel
from .permission import Permission
from .role import Role


class RolePermission(BaseModel):
    __tablename__ = "role_permissions"

    role_id = Column(PGUUID(as_uuid=True), nullable=False)
    permission_id = Column(PGUUID(as_uuid=True), nullable=False)

    __mapper_args__ = {
        "primary_key": [role_id, permission_id]
    }