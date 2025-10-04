"""
Tests for authentication methods of the JSON API Client.
"""

import pytest
import httpx
from doko.json_api_client import DokoApiClient
from doko.json_api_client.client import AsyncDokoApiClient


class TestAuthenticationSync:
    """Test authentication methods with sync client."""
    
    def test_get_api_info(self, api_client: DokoApiClient):
        """Test getting API information."""
        info = api_client.get_api_info()
        
        assert "name" in info
        assert info["name"] == "Doko REST API"
        assert info["version"] == "1.0"
        assert info["description"] == "RESTful API for Doppelkopf card game"
    
    def test_login_valid_credentials(self, api_client: DokoApiClient):
        """Test login with valid credentials."""
        result = api_client.login("rene", "123456789")
        
        assert result["success"] is True
        assert result["user"] == "rene"
        assert "set_cookie" in result
        assert api_client.session_token is not None
        
        # Verify cookie structure
        cookie_data = result["set_cookie"]
        assert "value" in cookie_data
        assert "expires" in cookie_data
        assert "httponly" in cookie_data
        assert cookie_data["httponly"] is True
    
    def test_login_invalid_credentials(self, api_client: DokoApiClient):
        """Test login with invalid credentials."""
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            api_client.login("invalid_user", "wrong_password")
        
        assert exc_info.value.response.status_code == 401
        assert api_client.session_token is None
    
    def test_logout(self, api_client: DokoApiClient):
        """Test logout."""
        # First login
        api_client.login("rene", "123456789")
        assert api_client.session_token is not None
        
        # Then logout
        result = api_client.logout()
        assert result["success"] is True
        assert "delete_cookie" in result
        assert api_client.session_token is None
    
    def test_logout_without_login(self, api_client: DokoApiClient):
        """Test logout without being logged in."""
        # Should still work even without being logged in
        result = api_client.logout()
        assert result["success"] is True


class TestAuthenticationAsync:
    """Test authentication methods with async client."""
    
    async def test_get_api_info(self, async_api_client: AsyncDokoApiClient):
        """Test getting API information."""
        info = await async_api_client.get_api_info()
        
        assert "name" in info
        assert info["name"] == "Doko REST API"
        assert info["version"] == "1.0"
        assert info["description"] == "RESTful API for Doppelkopf card game"
    
    async def test_login_valid_credentials(self, async_api_client: AsyncDokoApiClient):
        """Test login with valid credentials."""
        result = await async_api_client.login("rene", "123456789")
        
        assert result["success"] is True
        assert result["user"] == "rene"
        assert "set_cookie" in result
        assert async_api_client.session_token is not None
        
        # Verify cookie structure
        cookie_data = result["set_cookie"]
        assert "value" in cookie_data
        assert "expires" in cookie_data
        assert "httponly" in cookie_data
        assert cookie_data["httponly"] is True
    
    async def test_login_invalid_credentials(self, async_api_client: AsyncDokoApiClient):
        """Test login with invalid credentials."""
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await async_api_client.login("invalid_user", "wrong_password")
        
        assert exc_info.value.response.status_code == 401
        assert async_api_client.session_token is None
    
    async def test_logout(self, async_api_client: AsyncDokoApiClient):
        """Test logout."""
        # First login
        await async_api_client.login("rene", "123456789")
        assert async_api_client.session_token is not None
        
        # Then logout
        result = await async_api_client.logout()
        assert result["success"] is True
        assert "delete_cookie" in result
        assert async_api_client.session_token is None
    
    async def test_logout_without_login(self, async_api_client: AsyncDokoApiClient):
        """Test logout without being logged in."""
        # Should still work even without being logged in
        result = await async_api_client.logout()
        assert result["success"] is True