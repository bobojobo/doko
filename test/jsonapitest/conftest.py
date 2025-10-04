"""
API test fixtures and configuration.
"""

import os
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
import asyncio
from typing import AsyncGenerator

# Set up test environment before importing app
# Override database URL to use localhost instead of docker 'db' hostname
os.environ["doko__DB_URL"] = "postgresql+psycopg://postgres:password@localhost:5432/doko"

from doko.main import app, test_setup
from doko import db, orm
from doko.orm import Crud


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Setup database tables and test data for tests."""
    # Create all tables
    async with db.engine().begin() as conn:
        await conn.run_sync(Crud.metadata.create_all)
    
    # Add test data
    async with db.get_session() as session:
        await test_setup(session)
    
    yield
    
    # Cleanup after all tests
    async with db.engine().begin() as conn:
        await conn.run_sync(Crud.metadata.drop_all)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as client:
        yield client


@pytest.fixture
def client() -> TestClient:
    """Create a sync HTTP client for testing."""
    return TestClient(app)


@pytest.fixture
async def authenticated_client(async_client: AsyncClient) -> AsyncGenerator[AsyncClient, None]:
    """Create an authenticated async HTTP client for testing."""
    # Login with test credentials
    login_data = {
        "username": "rene", 
        "password": "123456789"
    }
    response = await async_client.post("/json/auth/login", json=login_data)
    
    # Extract session cookie if login successful
    if response.status_code == 200:
        response_data = response.json()
        if "set_cookie" in response_data and "success" in response_data:
            if response_data["success"]:
                cookie_data = response_data["set_cookie"]
                # The cookie_data is a dict containing the Cookie model fields
                session_token = cookie_data.get("value")
                if session_token:
                    async_client.cookies.set("session_token", session_token)
    
    yield async_client


@pytest.fixture
async def test_user_session_token(async_client: AsyncClient) -> str:
    """Get a session token for test user."""
    login_data = {
        "username": "rene",
        "password": "123456789"
    }
    response = await async_client.post("/json/auth/login", json=login_data)
    
    if response.status_code == 200:
        response_data = response.json()
        if "set_cookie" in response_data and "success" in response_data:
            if response_data["success"]:
                cookie_data = response_data["set_cookie"]
                session_token = cookie_data.get("value")
                if session_token:
                    return session_token
    
    raise Exception("Failed to get test user session token")