#!/usr/bin/env python3
"""Создание первого администратора для платформы"""

import os
import sys
import uuid
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

# Import models from auth-service (using dynamic import to avoid hyphen issues)
import importlib
import sys
import os

def import_model(service_name: str, module_name: str):
    """Dynamically import model from service with hyphen in name."""
    service_path = os.path.join("platform", "services", service_name, "src")
    sys.path.insert(0, service_path)
    try:
        return importlib.import_module(module_name)
    finally:
        sys.path.pop(0)

try:
    permission_mod = import_model("auth-service", "models.permission")
    role_mod = import_model("auth-service", "models.role")
    role_perm_mod = import_model("auth-service", "models.role_permission")
    user_mod = import_model("auth-service", "models.user")
    user_role_mod = import_model("auth-service", "models.user_role")

    Permission = permission_mod.Permission
    Role = role_mod.Role
    RolePermission = role_perm_mod.RolePermission
    User = user_mod.User
    UserRole = user_role_mod.UserRole
except ImportError as e:
    print(f"Failed to import models: {e}")
    raise

def create_admin_user(db_url: str, email: str, password: str, full_name: str = "Admin User"):
    """Create admin user with platform_admin role"""
    
    # Create engine and session
    engine = create_engine(db_url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User {email} already exists")
            return existing_user
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=password,  # In real app, this should be hashed
            full_name=full_name,
            role="platform_admin",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create platform_admin role if it doesn't exist
        platform_admin_role = db.query(Role).filter(Role.name == "platform_admin").first()
        if not platform_admin_role:
            platform_admin_role = Role(
                id=uuid.uuid4(),
                name="platform_admin",
                description="Platform administrator role",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(platform_admin_role)
            db.commit()
            db.refresh(platform_admin_role)
        
        # Create user-role mapping
        user_role = UserRole(
            user_id=user.id,
            role_id=platform_admin_role.id
        )
        db.add(user_role)
        
        # Create permissions for platform_admin role
        permissions = [
            "users.manage",
            "companies.manage",
            "partnerships.manage",
            "billing.manage",
            "settings.manage",
            "monitoring.view"
        ]
        
        for perm_name in permissions:
            permission = db.query(Permission).filter(Permission.name == perm_name).first()
            if not permission:
                permission = Permission(
                    id=uuid.uuid4(),
                    name=perm_name,
                    description=f"Manage {perm_name.replace('.', ' ')}",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(permission)
                db.commit()
                db.refresh(permission)
            
            # Create role-permission mapping
            role_permission = RolePermission(
                role_id=platform_admin_role.id,
                permission_id=permission.id
            )
            db.add(role_permission)
        
        db.commit()
        print(f"✅ Admin user created: {email}")
        return user
        
    except IntegrityError as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    # Get database URL from environment or use default
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://algo_user:password@postgres:5432/algorithmic_arts")
    
    # Default admin credentials
    admin_email = "admin@algorithmic-arts.ru"
    admin_password = "admin123"  # In production, this should be hashed
    
    print(f"Creating admin user: {admin_email}")
    create_admin_user(db_url, admin_email, admin_password)