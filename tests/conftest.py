import pytest
from fastapi.testclient import TestClient
import os
from dotenv import load_dotenv

from app.main import app

load_dotenv(".env.test")

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_item_data():
    """Sample item data for testing."""
    return {
        "name": "Test Item",
        "description": "A test item for unit testing",
        "price": 29.99,
    }
