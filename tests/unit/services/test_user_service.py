"""Unit tests for UserService."""
import pytest
from datetime import datetime, timezone
from app.models import User
from app.services.user_service import UserService
from app import db

@pytest.fixture
def user_service():
    """Fixture for UserService."""
    return UserService()

@pytest.fixture
def sample_user_data():
    """Fixture for sample user data."""
    return {
        'username': 'test_user',
        'email': 'test@example.com',
        'password': 'test_password'
    }

class TestUserService:
    """Test cases for UserService."""

    def test_create_user_success(self, init_database, user_service, sample_user_data):
        """Test successful user creation."""
        user = user_service.create_user(**sample_user_data)
        
        assert user.username == sample_user_data['username']
        assert user.email == sample_user_data['email']
        assert user.check_password(sample_user_data['password'])
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_create_user_duplicate_username(self, init_database, user_service, sample_user_data):
        """Test user creation with duplicate username."""
        user_service.create_user(**sample_user_data)
        
        with pytest.raises(ValueError) as exc_info:
            user_service.create_user(**sample_user_data)
        assert str(exc_info.value) == "Username already exists"

    def test_create_user_duplicate_email(self, init_database, user_service, sample_user_data):
        """Test user creation with duplicate email."""
        user_service.create_user(**sample_user_data)
        
        new_data = sample_user_data.copy()
        new_data['username'] = 'another_user'
        
        with pytest.raises(ValueError) as exc_info:
            user_service.create_user(**new_data)
        assert str(exc_info.value) == "Email already exists"

    def test_create_user_invalid_email(self, init_database, user_service):
        """Test user creation with invalid email format."""
        invalid_data = {
            'username': 'test_user',
            'email': 'invalid_email',
            'password': 'test_password'
        }
        
        with pytest.raises(ValueError) as exc_info:
            user_service.create_user(**invalid_data)
        assert str(exc_info.value) == "Invalid email format"

    def test_get_user_by_id_success(self, init_database, user_service, sample_user_data):
        """Test successfully getting user by ID."""
        created_user = user_service.create_user(**sample_user_data)
        db.session.add(created_user)
        db.session.commit()

        retrieved_user = user_service.get_user_by_id(created_user.id)
        assert retrieved_user == created_user
        assert retrieved_user.username == sample_user_data['username']

    def test_get_user_by_id_not_found(self, init_database, user_service):
        """Test getting non-existent user by ID."""
        with pytest.raises(ValueError) as exc_info:
            user_service.get_user_by_id(999)
        assert str(exc_info.value) == "User not found"

    def test_get_user_by_username(self, init_database, user_service, sample_user_data):
        """Test getting user by username."""
        created_user = user_service.create_user(**sample_user_data)
        db.session.add(created_user)
        db.session.commit()

        retrieved_user = user_service.get_user_by_username(sample_user_data['username'])
        assert retrieved_user == created_user

    def test_get_user_by_email(self, init_database, user_service, sample_user_data):
        """Test getting user by email."""
        created_user = user_service.create_user(**sample_user_data)
        db.session.add(created_user)
        db.session.commit()

        retrieved_user = user_service.get_user_by_email(sample_user_data['email'])
        assert retrieved_user == created_user

    def test_update_user_success(self, init_database, user_service, sample_user_data):
        """Test successful user update."""
        user = user_service.create_user(**sample_user_data)
        db.session.add(user)
        db.session.commit()
        
        update_data = {
            'email': 'updated@example.com',
            'password': 'new_password'
        }
        updated_user = user_service.update_user(user, update_data)
        
        assert updated_user.email == update_data['email']
        assert updated_user.check_password(update_data['password'])
        assert updated_user.updated_at > updated_user.created_at

    def test_update_user_duplicate_email(self, init_database, user_service, sample_user_data):
        """Test updating user with duplicate email."""
        # Create first user
        user1 = user_service.create_user(**sample_user_data)
        db.session.add(user1)
        
        # Create second user
        user2_data = sample_user_data.copy()
        user2_data['username'] = 'another_user'
        user2_data['email'] = 'another@example.com'
        user2 = user_service.create_user(**user2_data)
        db.session.add(user2)
        db.session.commit()
        
        # Try to update second user with first user's email
        with pytest.raises(ValueError) as exc_info:
            user_service.update_user(user2, {'email': sample_user_data['email']})
        assert str(exc_info.value) == "Email already exists"

    def test_delete_user(self, init_database, user_service, sample_user_data):
        """Test user deletion."""
        user = user_service.create_user(**sample_user_data)
        db.session.add(user)
        db.session.commit()
        
        user_service.delete_user(user)
        
        with pytest.raises(ValueError):
            user_service.get_user_by_id(user.id) 