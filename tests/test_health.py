"""Tests for health check endpoints."""


def test_root_health_check(client):
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_simple_health_check(client):
    """Test simple health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_detailed_health_check(client):
    """Test detailed v1 health check endpoint."""
    response = client.get("/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "IIC3964 Backend"


def test_very_detailed_health_check(client):
    """Test very detailed health check endpoint."""
    response = client.get("/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data
