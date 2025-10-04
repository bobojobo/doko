"""
Tests for group management methods of the JSON API Client.
"""

import pytest
from doko.json_api_client import DokoApiClient
from doko.json_api_client.client import AsyncDokoApiClient


class TestGroupManagementSync:
    """Test group management methods with sync client."""
    
    def test_list_groups(self, authenticated_api_client: DokoApiClient):
        """Test listing user's groups."""
        result = authenticated_api_client.list_groups()
        
        assert "groups" in result
        assert "user" in result
        assert result["user"] == "rene"
        assert isinstance(result["groups"], list)
    
    def test_create_group(self, authenticated_api_client: DokoApiClient):
        """Test creating a new group."""
        groupname = "testgroup_sync"
        
        result = authenticated_api_client.create_group(
            groupname=groupname,
            username_0="nadiem",
            username_1="florian",
            username_2="simon"
        )
        
        assert result["success"] is True
        assert result["group_name"] == groupname
    
    def test_create_group_minimal(self, authenticated_api_client: DokoApiClient):
        """Test creating a group with minimal parameters."""
        groupname = "minimal_group_sync"
        
        result = authenticated_api_client.create_group(
            groupname=groupname,
            username_0="nadiem",
            username_1="florian",
            username_2="simon"
        )
        
        assert result["success"] is True
        assert result["group_name"] == groupname
    
    def test_get_group(self, authenticated_api_client: DokoApiClient):
        """Test getting group details."""
        groupname = "detailstest_sync"
        
        # Create group first
        authenticated_api_client.create_group(
            groupname=groupname,
            username_0="nadiem",
            username_1="florian",
            username_2="simon"
        )
        
        # Get group details
        result = authenticated_api_client.get_group(groupname)
        
        assert result["name"] == groupname
        assert "players" in result
        assert "user" in result
        assert result["user"] == "rene"
        assert isinstance(result["players"], list)
    
    def test_create_and_list_groups(self, authenticated_api_client: DokoApiClient):
        """Test creating groups and then listing them."""
        groupname = "listtest_sync"
        
        # Get initial groups count
        initial_result = authenticated_api_client.list_groups()
        initial_count = len(initial_result["groups"])
        
        # Create a new group
        authenticated_api_client.create_group(
            groupname=groupname,
            username_0="nadiem",
            username_1="florian",
            username_2="simon"
        )
        
        # List groups again
        result = authenticated_api_client.list_groups()
        
        # Should have one more group
        assert len(result["groups"]) == initial_count + 1
        
        # Should contain our new group
        group_names = [group["name"] for group in result["groups"]]
        assert groupname in group_names


class TestGroupManagementAsync:
    """Test group management methods with async client."""
    
    async def test_list_groups(self, authenticated_async_api_client: AsyncDokoApiClient):
        """Test listing user's groups."""
        result = await authenticated_async_api_client.list_groups()
        
        assert "groups" in result
        assert "user" in result
        assert result["user"] == "rene"
        assert isinstance(result["groups"], list)
    
    async def test_create_group(self, authenticated_async_api_client: AsyncDokoApiClient):
        """Test creating a new group."""
        groupname = "testgroup_async"
        
        result = await authenticated_async_api_client.create_group(
            groupname=groupname,
            username_0="nadiem",
            username_1="florian",
            username_2="simon"
        )
        
        assert result["success"] is True
        assert result["group_name"] == groupname
    
    async def test_create_group_minimal(self, authenticated_async_api_client: AsyncDokoApiClient):
        """Test creating a group with minimal parameters."""
        groupname = "minimal_group_async"
        
        result = await authenticated_async_api_client.create_group(
            groupname=groupname,
            username_0="nadiem",
            username_1="florian",
            username_2="simon"
        )
        
        assert result["success"] is True
        assert result["group_name"] == groupname
    
    async def test_get_group(self, authenticated_async_api_client: AsyncDokoApiClient):
        """Test getting group details."""
        groupname = "detailstest_async"
        
        # Create group first
        await authenticated_async_api_client.create_group(
            groupname=groupname,
            username_0="nadiem",
            username_1="florian",
            username_2="simon"
        )
        
        # Get group details
        result = await authenticated_async_api_client.get_group(groupname)
        
        assert result["name"] == groupname
        assert "players" in result
        assert "user" in result
        assert result["user"] == "rene"
        assert isinstance(result["players"], list)
    
    async def test_create_and_list_groups(self, authenticated_async_api_client: AsyncDokoApiClient):
        """Test creating groups and then listing them."""
        groupname = "listtest_async"
        
        # Get initial groups count
        initial_result = await authenticated_async_api_client.list_groups()
        initial_count = len(initial_result["groups"])
        
        # Create a new group
        await authenticated_async_api_client.create_group(
            groupname=groupname,
            username_0="nadiem",
            username_1="florian",
            username_2="simon"
        )
        
        # List groups again
        result = await authenticated_async_api_client.list_groups()
        
        # Should have one more group
        assert len(result["groups"]) == initial_count + 1
        
        # Should contain our new group
        group_names = [group["name"] for group in result["groups"]]
        assert groupname in group_names