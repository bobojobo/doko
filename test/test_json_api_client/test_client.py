"""
Tests for the basic functionality and error handling of the JSON API Client.
"""

import pytest
import httpx
from doko.json_api_client import DokoApiClient
from doko.json_api_client.client import AsyncDokoApiClient


class TestClientBasics:
    """Test basic client functionality."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = DokoApiClient("http://localhost:8000")
        assert client.base_url == "http://localhost:8000"
        assert client.json_base_url == "http://localhost:8000/json"
        assert client.session_token is None
        client.close()
    
    def test_client_context_manager(self, test_server):
        """Test client as context manager."""
        with DokoApiClient(base_url=test_server.base_url) as client:
            info = client.get_api_info()
            assert "name" in info
    
    def test_async_client_initialization(self):
        """Test async client initialization."""
        client = AsyncDokoApiClient("http://localhost:8000")
        assert client.base_url == "http://localhost:8000"
        assert client.json_base_url == "http://localhost:8000/json"
        assert client.session_token is None
    
    async def test_async_client_context_manager(self, test_server):
        """Test async client as context manager."""
        async with AsyncDokoApiClient(base_url=test_server.base_url) as client:
            info = await client.get_api_info()
            assert "name" in info


class TestErrorHandling:
    """Test error handling in the client."""
    
    def test_invalid_server_url(self):
        """Test client with invalid server URL."""
        with DokoApiClient("http://nonexistent:9999") as client:
            with pytest.raises(httpx.ConnectError):
                client.get_api_info()
    
    async def test_async_invalid_server_url(self):
        """Test async client with invalid server URL."""
        async with AsyncDokoApiClient("http://nonexistent:9999") as client:
            with pytest.raises(httpx.ConnectError):
                await client.get_api_info()
    
    def test_unauthenticated_request(self, api_client: DokoApiClient):
        """Test making authenticated request without login."""
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            api_client.list_groups()
        
        # Should get a 403 Forbidden or similar auth error
        assert exc_info.value.response.status_code in [401, 403, 422]
    
    async def test_async_unauthenticated_request(self, async_api_client: AsyncDokoApiClient):
        """Test making authenticated request without login."""
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await async_api_client.list_groups()
        
        # Should get a 403 Forbidden or similar auth error
        assert exc_info.value.response.status_code in [401, 403, 422]


class TestCookieHandling:
    """Test cookie and session management."""
    
    def test_session_token_persistence(self, api_client: DokoApiClient):
        """Test that session token persists across requests."""
        # Login
        api_client.login("rene", "123456789")
        token_after_login = api_client.session_token
        assert token_after_login is not None
        
        # Make another authenticated request
        api_client.list_groups()
        
        # Token should be the same
        assert api_client.session_token == token_after_login
    
    async def test_async_session_token_persistence(self, async_api_client: AsyncDokoApiClient):
        """Test that session token persists across requests."""
        # Login
        await async_api_client.login("rene", "123456789")
        token_after_login = async_api_client.session_token
        assert token_after_login is not None
        
        # Make another authenticated request
        await async_api_client.list_groups()
        
        # Token should be the same
        assert async_api_client.session_token == token_after_login
    
    def test_session_token_cleared_on_logout(self, api_client: DokoApiClient):
        """Test that session token is cleared on logout."""
        # Login
        api_client.login("rene", "123456789")
        assert api_client.session_token is not None
        
        # Logout
        api_client.logout()
        assert api_client.session_token is None
    
    async def test_async_session_token_cleared_on_logout(self, async_api_client: AsyncDokoApiClient):
        """Test that session token is cleared on logout."""
        # Login
        await async_api_client.login("rene", "123456789")
        assert async_api_client.session_token is not None
        
        # Logout
        await async_api_client.logout()
        assert async_api_client.session_token is None


class TestRequestMethods:
    """Test internal request methods."""
    
    def test_cookies_without_session(self, api_client: DokoApiClient):
        """Test cookie handling without session token."""
        cookies = api_client._get_cookies()
        assert cookies == {}
    
    def test_cookies_with_session(self, api_client: DokoApiClient):
        """Test cookie handling with session token."""
        api_client.session_token = "test_token"
        cookies = api_client._get_cookies()
        assert cookies == {"session_token": "test_token"}
    
    async def test_async_cookies_without_session(self, async_api_client: AsyncDokoApiClient):
        """Test cookie handling without session token."""
        cookies = async_api_client._get_cookies()
        assert cookies == {}
    
    async def test_async_cookies_with_session(self, async_api_client: AsyncDokoApiClient):
        """Test cookie handling with session token."""
        async_api_client.session_token = "test_token"
        cookies = async_api_client._get_cookies()
        assert cookies == {"session_token": "test_token"}