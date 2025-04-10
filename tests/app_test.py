import os, sys
# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app


@pytest.fixture
def client():
    """
    A test client for the Flask application.
    This fixture sets up the Flask application for testing and provides a client
    to make requests to the application.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home(client):
    """
    Test the home route of the Flask application.
    This test checks if the home route returns a 200 status code.
    """
    response = client.get('/')
    assert response.status_code == 200


def test_liststock(client):
    """
    Test the liststock route of the Flask application.
    This test checks if the liststock route returns a 200 status code
    and if the response is a list of stocks with the expected structure.
    """
    response = client.get('/liststock')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert all("name" in item for item in data)


def test_salestock(client):
    """
    Test the salestock route of the Flask application.
    This test checks if the salestock route returns a 200 status code.
    """
    response = client.get('/salestock')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)