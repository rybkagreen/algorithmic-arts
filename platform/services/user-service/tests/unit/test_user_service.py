"""Unit tests for user service."""

import pytest
from unittest.mock import patch
from datetime import datetime
from uuid import UUID

from src.services.user_service import UserService
from src.schemas.user import UserCreate, UserOut


class TestUserService:
    """Unit tests for user service."""
    
    @pytest.fixture
    def user_service(self):
        return UserService()
    
    def test_user_creation(self, user_service):
        """Test user creation structure."""
        user_data = UserCreate(
            email="test@example.com",
            full_name="Test User",
            password="password123"
        )
        
        assert user_data.email == "test@example.com"
        assert user_data.full_name == "Test User"
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, user_service):
        """Test getting user by ID."""
        # Mock database
        with patch.object(user_service.user_repository, 'get_by_id') as mock_get:
            mock_user = UserOut(
                id=str(UUID("12345678-1234-5678-1234-567812345678")),
                email="test@example.com",
                full_name="Test User",
                company_id=None,
                role="free_user",
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            )
            mock_get.return_value = mock_user
            
            result = await user_service.get_user_by_id(UUID("12345678-1234-5678-1234-567812345678"))
            
            assert result.id == mock_user.id
            assert result.email == mock_user.email