"""
Tests for user management methods of the JSON API Client.
"""

import pytest
import httpx
from doko.json_api_client import DokoApiClient
from doko.json_api_client.client import AsyncDokoApiClient


class TestUserManagementSync:
    """Test user management methods with sync client."""
    
    def test_create_user_success(self, api_client: DokoApiClient):
        """Test creating a new user."""
        username = "testuser_sync"
        password = "testpassword123"
        
        result = api_client.create_user(username, password, password)
        
        assert result["success"] is True
        assert result["username"] == username
    
    def test_create_user_duplicate_username(self, api_client: DokoApiClient):
        """Test creating user with existing username."""
        # Try to create user with existing username
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            api_client.create_user("rene", "newpassword", "newpassword")
        
        assert exc_info.value.response.status_code == 409  # Conflict
    
    def test_create_user_password_mismatch(self, api_client: DokoApiClient):
        """Test creating user with mismatched passwords."""
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            api_client.create_user("testuser_mismatch", "password1", "password2")
        
        assert exc_info.value.response.status_code == 400  # Bad Request
    
    def test_create_user_then_login(self, api_client: DokoApiClient):
        """Test creating a user and then logging in with those credentials."""
        username = "logintest_sync"
        password = "loginpassword123"
        
        # Create user
        result = api_client.create_user(username, password, password)
        assert result["success"] is True
        
        # Login with new user
        login_result = api_client.login(username, password)
        assert login_result["success"] is True
        assert login_result["user"] == username
        assert api_client.session_token is not None


class TestUserManagementAsync:
    """Test user management methods with async client."""
    
    async def test_create_user_success(self, async_api_client: AsyncDokoApiClient):
        """Test creating a new user."""
        username = "testuser_async"
        password = "testpassword123"
        
        result = await async_api_client.create_user(username, password, password)
        
        assert result["success"] is True
        assert result["username"] == username
    
    async def test_create_user_duplicate_username(self, async_api_client: AsyncDokoApiClient):
        """Test creating user with existing username."""
        # Try to create user with existing username
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await async_api_client.create_user("rene", "newpassword", "newpassword")
        
        assert exc_info.value.response.status_code == 409  # Conflict
    
    async def test_create_user_password_mismatch(self, async_api_client: AsyncDokoApiClient):
        """Test creating user with mismatched passwords."""
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await async_api_client.create_user("testuser_mismatch_async", "password1", "password2")
        
        assert exc_info.value.response.status_code == 400  # Bad Request
    
    async def test_create_user_then_login(self, async_api_client: AsyncDokoApiClient):
        """Test creating a user and then logging in with those credentials."""
        username = "logintest_async"
        password = "loginpassword123"
        
        # Create user
        result = await async_api_client.create_user(username, password, password)
        assert result["success"] is True
        
        # Login with new user
        login_result = await async_api_client.login(username, password)
        assert login_result["success"] is True
        assert login_result["user"] == username
        assert async_api_client.session_token is not None