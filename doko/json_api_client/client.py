"""
Doko JSON API Client

A Python client for interacting with the Doko Doppelkopf game JSON API.
"""

import httpx
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin


class DokoApiClient:
    """Client for the Doko JSON API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the Doko API server
        """
        self.base_url = base_url.rstrip('/')
        self.json_base_url = f"{self.base_url}/json"
        self.session_token: Optional[str] = None
        self._client = httpx.Client()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def _get_cookies(self) -> Dict[str, str]:
        """Get cookies for authenticated requests."""
        if self.session_token:
            return {"session_token": self.session_token}
        return {}
    
    def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Make a request to the API."""
        url = urljoin(self.json_base_url + "/", endpoint.lstrip('/'))
        
        # Add cookies for authenticated requests
        if 'cookies' not in kwargs:
            kwargs['cookies'] = self._get_cookies()
        
        response = self._client.request(method, url, **kwargs)
        return response
    
    # Authentication methods
    def get_api_info(self) -> Dict[str, Any]:
        """Get API information."""
        response = self._request("GET", "/")
        response.raise_for_status()
        return response.json()
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login to the API.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Login response data
            
        Raises:
            httpx.HTTPStatusError: If login fails
        """
        data = {
            "username": username,
            "password": password
        }
        response = self._request("POST", "/auth/login", json=data)
        response.raise_for_status()
        
        result = response.json()
        
        # Store session token if login successful
        if result.get("success") and "set_cookie" in result:
            cookie_data = result["set_cookie"]
            self.session_token = cookie_data.get("value")
        
        return result
    
    def logout(self) -> Dict[str, Any]:
        """
        Logout from the API.
        
        Returns:
            Logout response data
        """
        response = self._request("POST", "/auth/logout")
        response.raise_for_status()
        
        result = response.json()
        
        # Clear session token
        if result.get("success"):
            self.session_token = None
        
        return result
    
    # User methods
    def create_user(self, username: str, password: str, password_validation: str) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            username: Username
            password: Password
            password_validation: Password confirmation
            
        Returns:
            User creation response data
        """
        data = {
            "username": username,
            "password": password,
            "password_validation": password_validation
        }
        response = self._request("POST", "/users", json=data)
        response.raise_for_status()
        return response.json()
    
    # Group methods
    def list_groups(self) -> Dict[str, Any]:
        """
        Get list of user's groups.
        
        Returns:
            Groups list response data
        """
        response = self._request("GET", "/groups")
        response.raise_for_status()
        return response.json()
    
    def create_group(self, groupname: str, username_0: str = "", 
                    username_1: str = "", username_2: str = "") -> Dict[str, Any]:
        """
        Create a new group.
        
        Args:
            groupname: Name of the group
            username_0: First additional player (optional)
            username_1: Second additional player (optional)
            username_2: Third additional player (optional)
            
        Returns:
            Group creation response data
        """
        data = {
            "groupname": groupname,
            "username_0": username_0,
            "username_1": username_1,
            "username_2": username_2
        }
        response = self._request("POST", "/groups", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_group(self, group_name: str) -> Dict[str, Any]:
        """
        Get group details including players.
        
        Args:
            group_name: Name of the group
            
        Returns:
            Group details response data
        """
        response = self._request("GET", f"/groups/{group_name}")
        response.raise_for_status()
        return response.json()
    
    # Game methods
    def list_games(self) -> Dict[str, Any]:
        """
        Get list of user's games.
        
        Returns:
            Games list response data
        """
        response = self._request("GET", "/games")
        response.raise_for_status()
        return response.json()
    
    def create_game(self, groupname: str) -> Dict[str, Any]:
        """
        Create/start a new game for a group.
        
        Args:
            groupname: Name of the group
            
        Returns:
            Game creation response data
        """
        data = {"groupname": groupname}
        response = self._request("POST", "/games", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_game(self, game_id: str) -> Dict[str, Any]:
        """
        Get current game state.
        
        Args:
            game_id: ID of the game
            
        Returns:
            Game state response data
        """
        response = self._request("GET", f"/games/{game_id}")
        response.raise_for_status()
        return response.json()
    
    def play_card(self, game_id: str, suit: str, rank: str) -> Dict[str, Any]:
        """
        Play a card in the game.
        
        Args:
            game_id: ID of the game
            suit: Card suit
            rank: Card rank
            
        Returns:
            Play card response data
        """
        data = {
            "suit": suit,
            "rank": rank
        }
        response = self._request("POST", f"/games/{game_id}/cards", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_hand(self, game_id: str) -> Dict[str, Any]:
        """
        Get player's current hand.
        
        Args:
            game_id: ID of the game
            
        Returns:
            Hand response data
        """
        response = self._request("GET", f"/games/{game_id}/hand")
        response.raise_for_status()
        return response.json()
    
    def get_stack(self, game_id: str) -> Dict[str, Any]:
        """
        Get current trick/stack.
        
        Args:
            game_id: ID of the game
            
        Returns:
            Stack response data
        """
        response = self._request("GET", f"/games/{game_id}/stack")
        response.raise_for_status()
        return response.json()
    
    def update_hand_order(self, game_id: str, card_ids: List[str]) -> Dict[str, Any]:
        """
        Update the order of cards in player's hand.
        
        Args:
            game_id: ID of the game
            card_ids: List of card IDs in the new order
            
        Returns:
            Update response data
        """
        data = {"card_ids": card_ids}
        response = self._request("POST", f"/games/{game_id}/hand/order", json=data)
        response.raise_for_status()
        return response.json()
    
    # Game Review methods
    def get_game_review(self, game_id: str) -> Dict[str, Any]:
        """
        Get game review/results.
        
        Args:
            game_id: ID of the game
            
        Returns:
            Game review response data
        """
        response = self._request("GET", f"/game-reviews/{game_id}")
        response.raise_for_status()
        return response.json()
    
    def mark_ready_for_next_game(self, status: str, groupname: str) -> Dict[str, Any]:
        """
        Mark player as ready for next game.
        
        Args:
            status: Player status
            groupname: Name of the group
            
        Returns:
            Ready status response data
        """
        data = {
            "status": status,
            "groupname": groupname
        }
        response = self._request("POST", "/game-reviews/ready", json=data)
        response.raise_for_status()
        return response.json()


# Async version of the client
class AsyncDokoApiClient:
    """Async client for the Doko JSON API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the async API client.
        
        Args:
            base_url: Base URL of the Doko API server
        """
        self.base_url = base_url.rstrip('/')
        self.json_base_url = f"{self.base_url}/json"
        self.session_token: Optional[str] = None
        self._client = httpx.AsyncClient()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    def _get_cookies(self) -> Dict[str, str]:
        """Get cookies for authenticated requests."""
        if self.session_token:
            return {"session_token": self.session_token}
        return {}
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Make a request to the API."""
        url = urljoin(self.json_base_url + "/", endpoint.lstrip('/'))
        
        # Add cookies for authenticated requests
        if 'cookies' not in kwargs:
            kwargs['cookies'] = self._get_cookies()
        
        response = await self._client.request(method, url, **kwargs)
        return response
    
    # All the same methods as the sync client but with async/await
    async def get_api_info(self) -> Dict[str, Any]:
        """Get API information."""
        response = await self._request("GET", "/")
        response.raise_for_status()
        return response.json()
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login to the API."""
        data = {
            "username": username,
            "password": password
        }
        response = await self._request("POST", "/auth/login", json=data)
        response.raise_for_status()
        
        result = response.json()
        
        # Store session token if login successful
        if result.get("success") and "set_cookie" in result:
            cookie_data = result["set_cookie"]
            self.session_token = cookie_data.get("value")
        
        return result
    
    async def logout(self) -> Dict[str, Any]:
        """Logout from the API."""
        response = await self._request("POST", "/auth/logout")
        response.raise_for_status()
        
        result = response.json()
        
        # Clear session token
        if result.get("success"):
            self.session_token = None
        
        return result
    
    async def create_user(self, username: str, password: str, password_validation: str) -> Dict[str, Any]:
        """Create a new user."""
        data = {
            "username": username,
            "password": password,
            "password_validation": password_validation
        }
        response = await self._request("POST", "/users", json=data)
        response.raise_for_status()
        return response.json()
    
    async def list_groups(self) -> Dict[str, Any]:
        """Get list of user's groups."""
        response = await self._request("GET", "/groups")
        response.raise_for_status()
        return response.json()
    
    async def create_group(self, groupname: str, username_0: str = "", 
                          username_1: str = "", username_2: str = "") -> Dict[str, Any]:
        """Create a new group."""
        data = {
            "groupname": groupname,
            "username_0": username_0,
            "username_1": username_1,
            "username_2": username_2
        }
        response = await self._request("POST", "/groups", json=data)
        response.raise_for_status()
        return response.json()
    
    async def get_group(self, group_name: str) -> Dict[str, Any]:
        """Get group details including players."""
        response = await self._request("GET", f"/groups/{group_name}")
        response.raise_for_status()
        return response.json()
    
    async def list_games(self) -> Dict[str, Any]:
        """Get list of user's games."""
        response = await self._request("GET", "/games")
        response.raise_for_status()
        return response.json()
    
    async def create_game(self, groupname: str) -> Dict[str, Any]:
        """Create/start a new game for a group."""
        data = {"groupname": groupname}
        response = await self._request("POST", "/games", json=data)
        response.raise_for_status()
        return response.json()
    
    async def get_game(self, game_id: str) -> Dict[str, Any]:
        """Get current game state."""
        response = await self._request("GET", f"/games/{game_id}")
        response.raise_for_status()
        return response.json()
    
    async def play_card(self, game_id: str, suit: str, rank: str) -> Dict[str, Any]:
        """Play a card in the game."""
        data = {
            "suit": suit,
            "rank": rank
        }
        response = await self._request("POST", f"/games/{game_id}/cards", json=data)
        response.raise_for_status()
        return response.json()
    
    async def get_hand(self, game_id: str) -> Dict[str, Any]:
        """Get player's current hand."""
        response = await self._request("GET", f"/games/{game_id}/hand")
        response.raise_for_status()
        return response.json()
    
    async def get_stack(self, game_id: str) -> Dict[str, Any]:
        """Get current trick/stack."""
        response = await self._request("GET", f"/games/{game_id}/stack")
        response.raise_for_status()
        return response.json()
    
    async def update_hand_order(self, game_id: str, card_ids: List[str]) -> Dict[str, Any]:
        """Update the order of cards in player's hand."""
        data = {"card_ids": card_ids}
        response = await self._request("POST", f"/games/{game_id}/hand/order", json=data)
        response.raise_for_status()
        return response.json()
    
    async def get_game_review(self, game_id: str) -> Dict[str, Any]:
        """Get game review/results."""
        response = await self._request("GET", f"/game-reviews/{game_id}")
        response.raise_for_status()
        return response.json()
    
    async def mark_ready_for_next_game(self, status: str, groupname: str) -> Dict[str, Any]:
        """Mark player as ready for next game."""
        data = {
            "status": status,
            "groupname": groupname
        }
        response = await self._request("POST", "/game-reviews/ready", json=data)
        response.raise_for_status()
        return response.json()