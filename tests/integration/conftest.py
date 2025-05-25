"""Pytest configuration file for integration tests."""
import pytest
from app import create_app, db
from app.models import User
from config import IntegrationTestingConfig

@pytest.fixture(scope='session')
def app():
    """Create application for integration tests."""
    app = create_app(IntegrationTestingConfig)
    return app

@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture(scope='function')
def init_database(app):
    """Initialize test database."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def test_user(init_database, app):
    """Create test user."""
    with app.app_context():
        user = User(
            username='test_user',
            email='test@example.com'
        )
        db.session.add(user)
        db.session.commit()
        return user 