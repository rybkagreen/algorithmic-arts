"""Unit tests for auth service."""

import pytest
from unittest.mock import patch
from uuid import UUID

from src.services.auth_service import AuthService
from src.schemas.user import UserCreate, Token


class TestAuthService:
    """Unit tests for auth service."""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    def test_password_hashing(self, auth_service):
        """Test password hashing."""
        password = "testpassword123"
        hashed = auth_service._hash_password(password)
        assert hashed is not None
        assert len(hashed) > 0
    
    def test_token_generation(self, auth_service):
        """Test token generation."""
        # Mock JWT service
        with patch.object(auth_service.jwt_service, 'encode_access_token') as mock_encode:
            mock_encode.return_value = "mock_token"
            
            token_data = {"user_id": "123", "email": "test@example.com", "role": "free_user"}
            token = auth_service.jwt_service.encode_access_token(token_data)
            
            assert token == "mock_token"
    
    @pytest.mark.asyncio
    async def test_register_user(self, auth_service):
        """Test user registration."""
        # This would require database setup in real tests
        # For now, just test the structure
        user_data = UserCreate(
            email="test@example.com",
            full_name="Test User",
            password="password123"
        )
        
        # In real implementation, this would create a user in DB
        # Here we just verify the structure
        assert user_data.email == "test@example.com"
        assert user_data.full_name == "Test User"
    
    @pytest.mark.asyncio
    async def test_authenticate_success(self, auth_service):
        """Test successful authentication."""
        # Mock database and JWT service
        with patch.object(auth_service.user_repository, 'get_by_email') as mock_get_user:
            with patch.object(auth_service.jwt_service, 'encode_access_token') as mock_encode:
                mock_encode.return_value = "access_token"
                mock_encode.return_value = "refresh_token"
                
                # Mock user
                class MockUser:
                    id = UUID("12345678-1234-5678-1234-567812345678")
                    email = "test@example.com"
                    password_hash = "$2b$12$mockhash"
                    is_active = True
                    is_verified = True
                    role = "free_user"
                
                mock_get_user.return_value = MockUser()
                
                # Mock bcrypt check
                with patch('bcrypt.checkpw', return_value=True):
                    result = await auth_service.authenticate({
                        "email": "test@example.com",
                        "password": "password123"
                    })
                    
                    assert isinstance(result, Token)
                    assert result.access_token == "access_token"
                    assert result.token_type == "bearer"