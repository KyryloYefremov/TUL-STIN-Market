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