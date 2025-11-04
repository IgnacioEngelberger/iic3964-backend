import pytest

from dotenv import load_dotenv


load_dotenv(".env.test")


@pytest.fixture
def test_always_passes():
    """Simple smoke test that always passes."""
    assert True
