"""
Tests for the FastAPI POC app.
Run locally with: pytest
These same tests are what GitHub Actions runs automatically on every push/PR.
"""

from fastapi.testclient import TestClient
from app.main import app, items_db

client = TestClient(app)


def setup_function():
    """Reset the in-memory DB before each test so tests don't leak state."""
    items_db.clear()


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the GitHub Actions POC API"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_item_not_found():
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_create_and_get_item():
    # create an item
    payload = {"name": "Keyboard", "price": 49.99, "in_stock": True}
    create_response = client.post("/items", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Keyboard"
    assert created["price"] == 49.99
    assert "id" in created

    # fetch it back
    item_id = created["id"]
    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Keyboard"


def test_create_item_missing_field():
    # "price" is required by the Item model, so this should fail validation
    response = client.post("/items", json={"name": "Broken Item"})
    assert response.status_code == 422
