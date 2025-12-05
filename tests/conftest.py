import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from tests.fixtures.data_fixtures import (
    get_mock_clinical_attention,
    get_mock_clinical_attention_with_relations,
    get_mock_gemini_response,
    get_mock_insurance_company,
    get_mock_patient,
    get_mock_resident_doctor,
    get_mock_supervisor_doctor,
)
from tests.fixtures.supabase_mock import MockSupabaseClient

# Load environment variables before importing the app


load_dotenv(".env.test")  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client."""
    return MockSupabaseClient()


@pytest.fixture
def mock_gemini():
    """Create a mock Gemini AI response."""
    return get_mock_gemini_response()


@pytest.fixture
def sample_item_data():
    """Sample item data for testing."""
    return {
        "name": "Test Item",
        "description": "A test item for unit testing",
        "price": 29.99,
    }


@pytest.fixture
def sample_patient():
    """Sample patient data."""
    return get_mock_patient()


@pytest.fixture
def sample_resident_doctor():
    """Sample resident doctor data."""
    return get_mock_resident_doctor()


@pytest.fixture
def sample_supervisor_doctor():
    """Sample supervisor doctor data."""
    return get_mock_supervisor_doctor()


@pytest.fixture
def sample_clinical_attention():
    """Sample clinical attention data."""
    return get_mock_clinical_attention()


@pytest.fixture
def sample_clinical_attention_with_relations():
    """Sample clinical attention with patient and doctor relations."""
    return get_mock_clinical_attention_with_relations()


@pytest.fixture
def sample_insurance_company():
    """Sample insurance company data."""
    return get_mock_insurance_company()
