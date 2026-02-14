"""User service for user service."""

from typing import List
import uuid

from .dependencies import get_db

from shared.logging import get_logger
from .repositories.user_repository import UserRepository
from .schemas.user import UserCreate, UserUpdate, UserOut, CompanyCreate, CompanyUpdate, CompanyOut
from .core.exceptions import UserNotFoundError

logger = get_logger("user-service")


class UserService:
    """User service."""
    
    def __init__(self):
        self.user_repository = UserRepository()
    
    async def create_user(self, user_data: UserCreate) -> UserOut:
        """Create new user."""
        # Check if user exists
        async with get_db() as db:
            existing_user = await self.user_repository.get_by_email(db, user_data.email)
            if existing_user:
                raise UserNotFoundError("User already exists")
        
        # Hash password (in real implementation, this would be done in auth service)
        # For user service, we assume password is already hashed by auth service
        
        # Create user
        user_data_dict = user_data.model_dump()
        user_data_dict['password_hash'] = ""  # Will be set by auth service
        
        async with get_db() as db:
            user = await self.user_repository.create_user(db, user_data_dict)
            
            # Return user data
            return UserOut(**self.user_repository.to_dict(user))
    
    async def get_user_by_id(self, user_id: uuid.UUID) -> UserOut:
        """Get user by ID."""
        async with get_db() as db:
            user = await self.user_repository.get_by_id(db, user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")
            
            return UserOut(**self.user_repository.to_dict(user))
    
    async def update_user(self, user_id: uuid.UUID, update_data: UserUpdate) -> UserOut:
        """Update user."""
        async with get_db() as db:
            updated_user = await self.user_repository.update_user(db, user_id, update_data.model_dump(exclude_unset=True))
            return UserOut(**self.user_repository.to_dict(updated_user))
    
    async def delete_user(self, user_id: uuid.UUID) -> None:
        """Delete user (soft delete)."""
        async with get_db() as db:
            await self.user_repository.soft_delete_user(db, user_id)
    
    async def create_company(self, company_data: CompanyCreate) -> CompanyOut:
        """Create new company."""
        async with get_db() as db:
            # Check if company exists by slug
            existing_company = await self.user_repository.get_company_by_slug(db, company_data.slug)
            if existing_company:
                raise UserNotFoundError("Company already exists")
            
            company_data_dict = company_data.model_dump()
            
            company = await self.user_repository.create_company(db, company_data_dict)
            
            return CompanyOut(**self.user_repository.to_company_dict(company))
    
    async def get_company_by_id(self, company_id: uuid.UUID) -> CompanyOut:
        """Get company by ID."""
        async with get_db() as db:
            company = await self.user_repository.get_company_by_id(db, company_id)
            if not company:
                raise UserNotFoundError(f"Company with ID {company_id} not found")
            
            return CompanyOut(**self.user_repository.to_company_dict(company))
    
    async def update_company(self, company_id: uuid.UUID, update_data: CompanyUpdate) -> CompanyOut:
        """Update company."""
        async with get_db() as db:
            updated_company = await self.user_repository.update_company(db, company_id, update_data.model_dump(exclude_unset=True))
            return CompanyOut(**self.user_repository.to_company_dict(updated_company))
    
    async def get_users_for_company(self, company_id: uuid.UUID) -> List[UserOut]:
        """Get all users for a company."""
        async with get_db() as db:
            users = await self.user_repository.get_users_by_company(db, company_id)
            return [UserOut(**self.user_repository.to_dict(user)) for user in users]
    
    async def assign_user_to_company(self, user_id: uuid.UUID, company_id: uuid.UUID) -> UserOut:
        """Assign user to company."""
        async with get_db() as db:
            user = await self.user_repository.update_user(db, user_id, {"company_id": str(company_id)})
            return UserOut(**self.user_repository.to_dict(user))