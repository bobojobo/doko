#!/usr/bin/env python3
"""
Example usage of the Doko JSON API Client.

This script demonstrates how to use the client to interact with the Doko API.
"""

import asyncio
from doko.json_api_client import DokoApiClient, AsyncDokoApiClient


def sync_example():
    """Example using the synchronous client."""
    print("=== Synchronous Client Example ===")
    
    # Create client
    with DokoApiClient("http://localhost:8000") as client:
        # Get API info
        info = client.get_api_info()
        print(f"API: {info['name']} v{info['version']}")
        
        # Create a new user
        try:
            result = client.create_user("example_user", "password123", "password123")
            print(f"Created user: {result['username']}")
        except Exception as e:
            print(f"User creation failed (may already exist): {e}")
        
        # Login
        try:
            login_result = client.login("example_user", "password123")
            if login_result["success"]:
                print(f"Logged in as: {login_result['user']}")
                
                # List groups
                groups = client.list_groups()
                print(f"User has {len(groups['groups'])} groups")
                
                # Create a group
                group_result = client.create_group("example_group")
                print(f"Created group: {group_result['group_name']}")
                
                # List groups again
                groups = client.list_groups()
                print(f"User now has {len(groups['groups'])} groups")
                
                # Logout
                logout_result = client.logout()
                print(f"Logged out: {logout_result['success']}")
            
        except Exception as e:
            print(f"Login failed: {e}")


async def async_example():
    """Example using the asynchronous client."""
    print("\n=== Asynchronous Client Example ===")
    
    # Create async client
    async with AsyncDokoApiClient("http://localhost:8000") as client:
        # Get API info
        info = await client.get_api_info()
        print(f"API: {info['name']} v{info['version']}")
        
        # Create a new user
        try:
            result = await client.create_user("async_example_user", "password123", "password123")
            print(f"Created user: {result['username']}")
        except Exception as e:
            print(f"User creation failed (may already exist): {e}")
        
        # Login
        try:
            login_result = await client.login("async_example_user", "password123")
            if login_result["success"]:
                print(f"Logged in as: {login_result['user']}")
                
                # List groups
                groups = await client.list_groups()
                print(f"User has {len(groups['groups'])} groups")
                
                # Create a group
                group_result = await client.create_group("async_example_group")
                print(f"Created group: {group_result['group_name']}")
                
                # List groups again
                groups = await client.list_groups()
                print(f"User now has {len(groups['groups'])} groups")
                
                # Logout
                logout_result = await client.logout()
                print(f"Logged out: {logout_result['success']}")
            
        except Exception as e:
            print(f"Login failed: {e}")


def main():
    """Run both sync and async examples."""
    print("Doko JSON API Client Examples")
    print("Make sure the Doko server is running on http://localhost:8000")
    print("-" * 50)
    
    # Run sync example
    sync_example()
    
    # Run async example
    asyncio.run(async_example())


if __name__ == "__main__":
    main()