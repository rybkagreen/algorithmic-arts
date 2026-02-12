from enum import Enum

from fastapi import Depends, HTTPException, status

from .jwt_validator import get_current_user


class Permission(str, Enum):
    COMPANY_READ = "company:read"
    COMPANY_WRITE = "company:write"
    COMPANY_DELETE = "company:delete"
    PARTNERSHIP_READ = "partnership:read"
    PARTNERSHIP_WRITE = "partnership:write"
    ANALYTICS_READ = "analytics:read"
    ADMIN_ACCESS = "admin:access"


ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "free_user": {
        Permission.COMPANY_READ,
        Permission.PARTNERSHIP_READ,
    },
    "paid_user": {
        Permission.COMPANY_READ,
        Permission.COMPANY_WRITE,
        Permission.PARTNERSHIP_READ,
        Permission.PARTNERSHIP_WRITE,
        Permission.ANALYTICS_READ,
    },
    "company_admin": {
        Permission.COMPANY_READ,
        Permission.COMPANY_WRITE,
        Permission.COMPANY_DELETE,
        Permission.PARTNERSHIP_READ,
        Permission.PARTNERSHIP_WRITE,
        Permission.ANALYTICS_READ,
    },
    "platform_admin": set(Permission),  # Все права
}


def require_permission(permission: Permission):
    """Dependency factory для проверки прав."""
    async def check_permission(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "free_user")
        allowed = ROLE_PERMISSIONS.get(user_role, set())
        if permission not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется разрешение: {permission.value}"
            )
        return current_user
    return check_permission