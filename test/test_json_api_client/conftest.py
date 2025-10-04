"""
Test configuration for JSON API Client tests.
"""

import os
import pytest
import asyncio
from typing import AsyncGenerator

# Set up test environment before importing app
# Override database URL to use localhost instead of docker 'db' hostname
os.environ["doko__DB_URL"] = "postgresql+psycopg://postgres:password@localhost:5432/doko"
# Disable database reset on startup for tests (we handle DB setup in fixtures)
os.environ["doko__RESET_DB_ON_STARTUP"] = "False"

from doko.main import app, test_setup
from doko import db, orm
from doko.orm import Crud
from doko.json_api_client import DokoApiClient
from doko.json_api_client.client import AsyncDokoApiClient

import uvicorn
import threading
import time


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


class TestServer:
    """Test server manager for running the API during tests."""
    
    def __init__(self, host="127.0.0.1", port=8001):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.base_url = f"http://{host}:{port}"
    
    def start(self):
        """Start the test server in a separate thread."""
        def run_server():
            config = uvicorn.Config(
                app=app,
                host=self.host,
                port=self.port,
                log_level="error",  # Reduce log noise during tests
                access_log=False
            )
            self.server = uvicorn.Server(config)
            asyncio.run(self.server.serve())
        
        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()
        
        # Wait for server to start
        max_attempts = 50
        for _ in range(max_attempts):
            try:
                import httpx
                with httpx.Client() as client:
                    response = client.get(f"{self.base_url}/json/")
                    if response.status_code == 200:
                        break
            except:
                pass
            time.sleep(0.1)
        else:
            raise RuntimeError("Test server failed to start")
    
    def stop(self):
        """Stop the test server."""
        if self.server:
            self.server.should_exit = True


@pytest.fixture(scope="session")
def test_server():
    """Start a test server for client tests."""
    server = TestServer()
    server.start()
    yield server
    server.stop()


@pytest.fixture
def api_client(test_server):
    """Create a sync API client for testing."""
    with DokoApiClient(base_url=test_server.base_url) as client:
        yield client


@pytest.fixture
async def async_api_client(test_server):
    """Create an async API client for testing."""
    async with AsyncDokoApiClient(base_url=test_server.base_url) as client:
        yield client


@pytest.fixture
async def authenticated_api_client(test_server):
    """Create an authenticated sync API client for testing."""
    with DokoApiClient(base_url=test_server.base_url) as client:
        # Login with test user
        client.login("rene", "123456789")
        yield client


@pytest.fixture
async def authenticated_async_api_client(test_server):
    """Create an authenticated async API client for testing."""
    async with AsyncDokoApiClient(base_url=test_server.base_url) as client:
        # Login with test user
        await client.login("rene", "123456789")
        yield client