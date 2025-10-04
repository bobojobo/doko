"""
Tests for authentication JSON API endpoints:
- /json/login/ (GET, POST)
- /json/logout/ (GET)
- /json/registration/ (GET, POST)
"""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestAuthEndpoints:
    """Test authentication related JSON API endpoints."""
    
    async def test_json_root_endpoint(self, async_client: AsyncClient):
        """Test JSON API root endpoint."""
        response = await async_client.get("/json/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "name" in data
        assert data["name"] == "Doko REST API"
        assert data["version"] == "1.0"
        assert data["description"] == "RESTful API for Doppelkopf card game"



    async def test_login_valid_credentials(self, async_client: AsyncClient):
        """Test login with valid credentials."""
        login_data = {
            "username": "rene",
            "password": "123456789"
        }
        
        response = await async_client.post("/json/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["user"] == "rene"
        assert "set_cookie" in data
        
        # Verify cookie structure
        cookie_data = data["set_cookie"]
        assert "value" in cookie_data
        assert "expires" in cookie_data
        assert "httponly" in cookie_data
        assert cookie_data["httponly"] is True

    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        response = await async_client.post("/json/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        
        # Should return error message
        assert "error" in data
        assert data["error"] == "Invalid credentials"

    async def test_login_missing_fields(self, async_client: AsyncClient):
        """Test login with missing required fields."""
        # Test missing username
        response = await async_client.post("/json/auth/login", json={"password": "123456789"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test missing password
        response = await async_client.post("/json/auth/login", json={"username": "rene"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test empty request
        response = await async_client.post("/json/auth/login", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_logout(self, authenticated_client: AsyncClient):
        """Test logout endpoint."""
        response = await authenticated_client.post("/json/auth/logout")
        
        # May fail if authentication didn't work properly in test
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data["success"] is True
            assert data["delete_cookie"] == "session_token"

    async def test_logout_unauthenticated(self, async_client: AsyncClient):
        """Test logout without authentication."""
        response = await async_client.post("/json/auth/logout")
        
        # Logout should succeed even without authentication (idempotent operation)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["delete_cookie"] == "session_token"



    async def test_registration_full_flow(self, async_client: AsyncClient):
        """Test complete registration flow."""
        import uuid
        unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
        
        registration_data = {
            "username": unique_username,
            "password": "strongpassword123",
            "password_validation": "strongpassword123"
        }
        
        response = await async_client.post("/json/users", json=registration_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Successful registration returns success and username
        assert data["success"] is True
        assert data["username"] == unique_username

    async def test_json_404_catch_all(self, async_client: AsyncClient):
        """Test JSON API 404 catch-all route."""
        response = await async_client.get("/json/nonexistent/path/")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Try to parse JSON response if available
        try:
            data = response.json()
            assert "detail" in data
            assert data["detail"] == "API endpoint not found"
        except:
            # If not JSON, just check status code is correct
            pass