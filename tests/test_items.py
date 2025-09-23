from fastapi.testclient import TestClient


def test_get_items(client: TestClient):
    """Test getting all items."""
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # We have 2 mock items


def test_get_item_by_id(client: TestClient):
    """Test getting a specific item by ID."""
    response = client.get("/api/v1/items/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Item 1"
    assert data["price"] == 10.99


def test_get_item_not_found(client: TestClient):
    """Test getting a non-existent item."""
    response = client.get("/api/v1/items/999")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Item not found"


def test_create_item(client: TestClient, sample_item_data):
    """Test creating a new item."""
    response = client.post("/api/v1/items/", json=sample_item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_item_data["name"]
    assert data["description"] == sample_item_data["description"]
    assert data["price"] == sample_item_data["price"]
    assert "id" in data


def test_create_item_invalid_data(client: TestClient):
    """Test creating an item with invalid data."""
    invalid_data = {
        "name": "Test Item",
        # Missing required fields
    }
    response = client.post("/api/v1/items/", json=invalid_data)
    assert response.status_code == 422  # Validation error


def test_create_item_negative_price(client: TestClient):
    """Test creating an item with negative price."""
    invalid_data = {
        "name": "Test Item",
        "description": "Test description",
        "price": -10.0,
    }
    response = client.post("/api/v1/items/", json=invalid_data)
    # This should still work as we don't have validation for negative prices
    # You might want to add this validation in your actual implementation
    assert response.status_code == 200
