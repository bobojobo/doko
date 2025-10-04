#!/usr/bin/env python3
"""
Simple demonstration of the Doko JSON API Client working.
This just tests the basic functionality without a full server.
"""

from doko.json_api_client import DokoApiClient, AsyncDokoApiClient
import asyncio


def demo_sync_client():
    """Demo sync client - basic functionality."""
    print("=== Sync Client Demo ===")
    
    # Test client initialization
    client = DokoApiClient("http://localhost:8000")
    print(f"✓ Client initialized with base URL: {client.base_url}")
    print(f"✓ JSON API URL: {client.json_base_url}")
    print(f"✓ Session token (initially None): {client.session_token}")
    
    # Test cookies without session
    cookies = client._get_cookies()
    print(f"✓ Cookies without session: {cookies}")
    
    # Test cookies with session
    client.session_token = "test_token_123"
    cookies = client._get_cookies()
    print(f"✓ Cookies with session: {cookies}")
    
    # Clear session
    client.session_token = None
    print(f"✓ Session cleared: {client.session_token}")
    
    client.close()
    print("✓ Client closed successfully")


async def demo_async_client():
    """Demo async client - basic functionality."""
    print("\n=== Async Client Demo ===")
    
    # Test client initialization
    client = AsyncDokoApiClient("http://localhost:8000")
    print(f"✓ Async client initialized with base URL: {client.base_url}")
    print(f"✓ JSON API URL: {client.json_base_url}")
    print(f"✓ Session token (initially None): {client.session_token}")
    
    # Test cookies without session
    cookies = client._get_cookies()
    print(f"✓ Cookies without session: {cookies}")
    
    # Test cookies with session
    client.session_token = "async_test_token_456"
    cookies = client._get_cookies()
    print(f"✓ Cookies with session: {cookies}")
    
    # Clear session
    client.session_token = None
    print(f"✓ Session cleared: {client.session_token}")
    
    await client.close()
    print("✓ Async client closed successfully")


def demo_context_managers():
    """Demo context manager usage."""
    print("\n=== Context Manager Demo ===")
    
    # Sync context manager
    with DokoApiClient("http://localhost:8000") as client:
        print(f"✓ Sync client in context manager: {client.base_url}")
    print("✓ Sync client automatically closed")


async def demo_async_context_managers():
    """Demo async context manager usage."""
    # Async context manager
    async with AsyncDokoApiClient("http://localhost:8000") as client:
        print(f"✓ Async client in context manager: {client.base_url}")
    print("✓ Async client automatically closed")


def main():
    """Run all demos."""
    print("Doko JSON API Client - Basic Functionality Demo")
    print("=" * 50)
    
    # Test basic functionality without requiring a server
    demo_sync_client()
    asyncio.run(demo_async_client())
    demo_context_managers()
    asyncio.run(demo_async_context_managers())
    
    print("\n" + "=" * 50)
    print("✓ All demos completed successfully!")
    print("\nThe Doko JSON API Client is ready to use!")
    print("\nTo test against a live server:")
    print("1. Start the database: just db-up")
    print("2. Start the API server: uv run uvicorn doko.main:app --reload")
    print("3. Run: uv run python doko/json_api_client/example.py")


if __name__ == "__main__":
    main()