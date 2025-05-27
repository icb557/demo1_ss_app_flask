"""Pytest configuration file."""
import pytest
from app import create_app, db
from app.models import User
from config import IntegrationTestingConfig

@pytest.fixture
def app():
    """Create application for the tests."""
    app = create_app(IntegrationTestingConfig)
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    """Initialize test database."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_user(init_database, app):
    """Create test user."""
    with app.app_context():
        user = User(
            username='test_user',
            email='test@example.com',
            password='password123'
        )
        db.session.add(user)
        db.session.commit()
        return user 