import pytest
from app import app

@pytest.fixture
def client():
    # Create a test client using Flask's built-in testing tools
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test that the health check endpoint is working."""
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}

def test_home_page(client):
    """Test that the frontend UI route exists."""
    response = client.get('/')
    assert response.status_code == 200