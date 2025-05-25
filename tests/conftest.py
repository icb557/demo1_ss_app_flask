"""Pytest configuration file."""
import os
import tempfile
import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    """Create application for the tests."""
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False
    })

    with app.app_context():
        db.create_all()
        yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()

@pytest.fixture
def test_user():
    """Create test user."""
    user = User(
        username='test_user',
        email='test@example.com'
    )
    db.session.add(user)
    db.session.commit()
    return user 