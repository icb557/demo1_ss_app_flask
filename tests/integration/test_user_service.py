"""Integration tests for UserService."""
import pytest
from datetime import datetime, timezone
from app.services.user_service import UserService
from app.models import User
from app import db

def test_create_user(init_database, app):
    """Test user creation with UserService."""
    with app.app_context():
        service = UserService()
        
        # Test successful creation
        user = service.create_user(
            username='test_user',
            email='test@example.com',
            password='test_password'
        )
        
        assert user.username == 'test_user'
        assert user.email == 'test@example.com'
        assert user.check_password('test_password')
        
        # Test duplicate username
        with pytest.raises(ValueError, match="Username already exists"):
            service.create_user(
                username='test_user',
                email='another@example.com',
                password='another_password'
            )
        
        # Test duplicate email
        with pytest.raises(ValueError, match="Email already exists"):
            service.create_user(
                username='another_user',
                email='test@example.com',
                password='another_password'
            )
        
        # Test invalid email format
        with pytest.raises(ValueError, match="Invalid email format"):
            service.create_user(
                username='invalid_email_user',
                email='invalid_email',
                password='test_password'
            )

def test_get_user_methods(init_database, app):
    """Test methods to retrieve users."""
    with app.app_context():
        service = UserService()
        
        # Create a test user
        user = service.create_user(
            username='get_test_user',
            email='get_test@example.com',
            password='test_password'
        )
        
        # Test get by ID
        retrieved_user = service.get_user_by_id(user.id)
        assert retrieved_user.id == user.id
        assert retrieved_user.username == user.username
        
        # Test get by username
        retrieved_user = service.get_user_by_username('get_test_user')
        assert retrieved_user.id == user.id
        assert retrieved_user.email == user.email
        
        # Test get by email
        retrieved_user = service.get_user_by_email('get_test@example.com')
        assert retrieved_user.id == user.id
        assert retrieved_user.username == user.username
        
        # Test not found cases
        with pytest.raises(ValueError, match="User not found"):
            service.get_user_by_id(9999)
        
        with pytest.raises(ValueError, match="User not found"):
            service.get_user_by_username('nonexistent_user')
            
        with pytest.raises(ValueError, match="User not found"):
            service.get_user_by_email('nonexistent@example.com')

def test_update_user(init_database, app):
    """Test updating user information."""
    with app.app_context():
        service = UserService()
        
        # Create test users
        user1 = service.create_user(
            username='update_test_user1',
            email='update_test1@example.com',
            password='test_password'
        )
        
        user2 = service.create_user(
            username='update_test_user2',
            email='update_test2@example.com',
            password='test_password'
        )
        
        # Test updating email
        updated_user = service.update_user(user1, {
            'email': 'new_email@example.com'
        })
        assert updated_user.email == 'new_email@example.com'
        
        # Test updating password
        updated_user = service.update_user(user1, {
            'password': 'new_password'
        })
        assert updated_user.check_password('new_password')
        
        # Test updating to existing email
        with pytest.raises(ValueError, match="Email already exists"):
            service.update_user(user1, {
                'email': 'update_test2@example.com'
            })

def test_delete_user(init_database, app):
    """Test user deletion."""
    with app.app_context():
        service = UserService()
        
        # Create a test user
        user = service.create_user(
            username='delete_test_user',
            email='delete_test@example.com',
            password='test_password'
        )
        
        # Delete the user
        service.delete_user(user)
        
        # Verify user is deleted
        with pytest.raises(ValueError, match="User not found"):
            service.get_user_by_id(user.id) 