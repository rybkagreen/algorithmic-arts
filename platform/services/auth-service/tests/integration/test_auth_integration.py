"""Integration tests for auth service."""

import pytest
import httpx

# Test configuration
BASE_URL = "http://localhost:8001"

@pytest.fixture(scope="session")
def client():
    """Create test client."""
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        yield client

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "auth-service"

@pytest.mark.asyncio
async def test_register_user(client):
    """Test user registration."""
    # Test data
    user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "password123"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert "Регистрация успешна" in data["message"]

@pytest.mark.asyncio
async def test_login_user(client):
    """Test user login (requires registered user)."""
    # First register a user
    user_data = {
        "email": "login-test@example.com",
        "full_name": "Login Test User",
        "password": "password123"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Then try to login
    login_data = {
        "email": "login-test@example.com",
        "password": "password123"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_refresh_token(client):
    """Test token refresh (requires valid refresh token)."""
    # This would require a more complex setup with actual tokens
    # For now, just test the endpoint structure
    response = client.post("/auth/refresh", json={"refresh_token": "dummy_token"})
    # Should return 401 for invalid token
    assert response.status_code == 401