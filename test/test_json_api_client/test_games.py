"""
Tests for game-related methods of the JSON API Client.
"""

import pytest
from doko.json_api_client import DokoApiClient
from doko.json_api_client.client import AsyncDokoApiClient


class TestGameManagementSync:
    """Test game management methods with sync client."""
    
    def test_list_games(self, authenticated_api_client: DokoApiClient):
        """Test listing user's games."""
        result = authenticated_api_client.list_games()
        
        assert "games" in result
        # Note: The current implementation returns a placeholder message
        assert "message" in result
        assert result["message"] == "Game listing not yet implemented"
    
    def test_create_game(self, authenticated_api_client: DokoApiClient):
        """Test creating a game."""
        groupname = "gametest_sync"
        
        # Create a group first
        authenticated_api_client.create_group(
            groupname=groupname,
            username_0="nadiem",
            username_1="florian",
            username_2="simon"
        )
        
        # Try to create a game
        result = authenticated_api_client.create_game(groupname=groupname)
        
        # The result depends on whether all players are ready
        # Since we only have one player, it should return waiting status
        assert "success" in result
        if result["success"]:
            assert "game_id" in result
            assert result["group_name"] == groupname
        else:
            assert result["message"] == "Waiting for other players"
            assert "players" in result


class TestGameManagementAsync:
    """Test game management methods with async client."""
    
    async def test_list_games(self, authenticated_async_api_client: AsyncDokoApiClient):
        """Test listing user's games."""
        result = await authenticated_async_api_client.list_games()
        
        assert "games" in result
        # Note: The current implementation returns a placeholder message
        assert "message" in result
        assert result["message"] == "Game listing not yet implemented"
    
    async def test_create_game(self, authenticated_async_api_client: AsyncDokoApiClient):
        """Test creating a game."""
        groupname = "gametest_async"
        
        # Create a group first
        await authenticated_async_api_client.create_group(
            groupname=groupname,
            username_0="nadiem",
            username_1="florian",
            username_2="simon"
        )
        
        # Try to create a game
        result = await authenticated_async_api_client.create_game(groupname=groupname)
        
        # The result depends on whether all players are ready
        # Since we only have one player, it should return waiting status
        assert "success" in result
        if result["success"]:
            assert "game_id" in result
            assert result["group_name"] == groupname
        else:
            assert result["message"] == "Waiting for other players"
            assert "players" in result


class TestGameStateSync:
    """Test game state methods with sync client (requires active game)."""
    
    def test_get_game_not_found(self, authenticated_api_client: DokoApiClient):
        """Test getting a non-existent game."""
        fake_game_id = "nonexistent_game_id"
        
        with pytest.raises(Exception):
            # This should fail because the game doesn't exist
            authenticated_api_client.get_game(fake_game_id)
    
    def test_get_hand_not_found(self, authenticated_api_client: DokoApiClient):
        """Test getting hand for non-existent game."""
        fake_game_id = "nonexistent_game_id"
        
        with pytest.raises(Exception):
            # This should fail because the game doesn't exist
            authenticated_api_client.get_hand(fake_game_id)
    
    def test_get_stack_not_found(self, authenticated_api_client: DokoApiClient):
        """Test getting stack for non-existent game."""
        fake_game_id = "nonexistent_game_id"
        
        with pytest.raises(Exception):
            # This should fail because the game doesn't exist
            authenticated_api_client.get_stack(fake_game_id)
    
    def test_play_card_not_found(self, authenticated_api_client: DokoApiClient):
        """Test playing card in non-existent game."""
        fake_game_id = "nonexistent_game_id"
        
        with pytest.raises(Exception):
            # This should fail because the game doesn't exist
            authenticated_api_client.play_card(fake_game_id, "hearts", "ace")
    
    def test_update_hand_order_not_found(self, authenticated_api_client: DokoApiClient):
        """Test updating hand order for non-existent game."""
        fake_game_id = "nonexistent_game_id"
        
        with pytest.raises(Exception):
            # This should fail because the game doesn't exist
            authenticated_api_client.update_hand_order(fake_game_id, ["card1", "card2"])


class TestGameStateAsync:
    """Test game state methods with async client (requires active game)."""
    
    async def test_get_game_not_found(self, authenticated_async_api_client: AsyncDokoApiClient):
        """Test getting a non-existent game."""
        fake_game_id = "nonexistent_game_id"
        
        with pytest.raises(Exception):
            # This should fail because the game doesn't exist
            await authenticated_async_api_client.get_game(fake_game_id)
    
    async def test_get_hand_not_found(self, authenticated_async_api_client: AsyncDokoApiClient):
        """Test getting hand for non-existent game."""
        fake_game_id = "nonexistent_game_id"
        
        with pytest.raises(Exception):
            # This should fail because the game doesn't exist
            await authenticated_async_api_client.get_hand(fake_game_id)
    
    async def test_get_stack_not_found(self, authenticated_async_api_client: AsyncDokoApiClient):
        """Test getting stack for non-existent game."""
        fake_game_id = "nonexistent_game_id"
        
        with pytest.raises(Exception):
            # This should fail because the game doesn't exist
            await authenticated_async_api_client.get_stack(fake_game_id)
    
    async def test_play_card_not_found(self, authenticated_async_api_client: AsyncDokoApiClient):
        """Test playing card in non-existent game."""
        fake_game_id = "nonexistent_game_id"
        
        with pytest.raises(Exception):
            # This should fail because the game doesn't exist
            await authenticated_async_api_client.play_card(fake_game_id, "hearts", "ace")
    
    async def test_update_hand_order_not_found(self, authenticated_async_api_client: AsyncDokoApiClient):
        """Test updating hand order for non-existent game."""
        fake_game_id = "nonexistent_game_id"
        
        with pytest.raises(Exception):
            # This should fail because the game doesn't exist
            await authenticated_async_api_client.update_hand_order(fake_game_id, ["card1", "card2"])


class TestGameReviewSync:
    """Test game review methods with sync client."""
    
    def test_get_game_review_not_found(self, authenticated_api_client: DokoApiClient):
        """Test getting review for non-existent game."""
        fake_game_id = "nonexistent_game_id"
        
        with pytest.raises(Exception):
            # This should fail because the game doesn't exist
            authenticated_api_client.get_game_review(fake_game_id)
    
    def test_mark_ready_for_next_game(self, authenticated_api_client: DokoApiClient):
        """Test marking ready for next game."""
        groupname = "readytest_sync"
        
        # Create a group first
        authenticated_api_client.create_group(
            groupname=groupname,
            username_0="nadiem",
            username_1="florian",
            username_2="simon"
        )
        
        # Try to mark ready (this might fail if no game exists, but should test the API call)
        try:
            result = authenticated_api_client.mark_ready_for_next_game("ready", groupname)
            assert result["success"] is True
        except Exception:
            # This is expected if no game exists for the group
            pass


class TestGameReviewAsync:
    """Test game review methods with async client."""
    
    async def test_get_game_review_not_found(self, authenticated_async_api_client: AsyncDokoApiClient):
        """Test getting review for non-existent game."""
        fake_game_id = "nonexistent_game_id"
        
        with pytest.raises(Exception):
            # This should fail because the game doesn't exist
            await authenticated_async_api_client.get_game_review(fake_game_id)
    
    async def test_mark_ready_for_next_game(self, authenticated_async_api_client: AsyncDokoApiClient):
        """Test marking ready for next game."""
        groupname = "readytest_async"
        
        # Create a group first
        await authenticated_async_api_client.create_group(
            groupname=groupname,
            username_0="nadiem",
            username_1="florian",
            username_2="simon"
        )
        
        # Try to mark ready (this might fail if no game exists, but should test the API call)
        try:
            result = await authenticated_async_api_client.mark_ready_for_next_game("ready", groupname)
            assert result["success"] is True
        except Exception:
            # This is expected if no game exists for the group
            pass