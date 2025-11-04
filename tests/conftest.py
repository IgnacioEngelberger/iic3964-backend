import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv(".env.test")
from app.main import app


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
