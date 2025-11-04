import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# Load environment variables before importing the app
load_dotenv(".env.test")

# noqa: E402 → tells flake8 to ignore "import not at top of file"
from app.main import app  # noqa: E402


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
