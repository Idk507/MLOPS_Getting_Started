from app import app
import pytest

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_hello(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Hello, GitHub Actions!' in response.data
