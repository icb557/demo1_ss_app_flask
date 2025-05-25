"""Unit tests for UserService."""
import pytest
from datetime import datetime, timezone
from app.models import User
from app.services.user_service import UserService
from app import db

class TestUserService:
    """Test cases for UserService."""

    def test_create_user(self):
        """Test user creation."""
        user_data = {
            'username': 'test_user',
            'email': 'test@example.com',
            'password': 'test_password'
        }
        user_service = UserService()
        user = user_service.create_user(**user_data)
        
        assert user.username == user_data['username']
        assert user.email == user_data['email']
        assert user.check_password(user_data['password'])

    def test_get_user_by_id(self):
        """Test getting user by ID."""
        user_service = UserService()
        user = User(username='test_user', email='test@example.com', password='test_password')
        db.session.add(user)
        db.session.commit()

        retrieved_user = user_service.get_user_by_id(user.id)
        assert retrieved_user == user

    def test_update_user(self):
        """Test updating user information."""
        user_service = UserService()
        user = User(username='test_user', email='test@example.com', password='test_password')
        
        update_data = {
            'email': 'updated@example.com'
        }
        updated_user = user_service.update_user(user, update_data)
        assert updated_user.email == update_data['email'] 