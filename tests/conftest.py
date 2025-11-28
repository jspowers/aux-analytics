import pytest
from app import create_app

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    app.config['APP_PASSWORD'] = 'testpass'
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client"""
    with client.session_transaction() as session:
        session['authenticated'] = True
    return client
