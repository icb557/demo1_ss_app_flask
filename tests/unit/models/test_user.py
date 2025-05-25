"""Test cases for User model."""
import pytest
from app.models import User

def test_new_user():
    """Test creating a new user."""
    user = User(
        username='testuser',
        email='test@test.com',
        password='testpass123'
    )
    
    assert user.username == 'testuser'
    assert user.email == 'test@test.com'
    assert user.password_hash is not None  # Password should be hashed
    assert user.check_password('testpass123')  # Should verify the password

def test_user_representation():
    """Test the string representation of a user."""
    user = User(username='testuser', email='test@test.com')
    assert str(user) == '<User testuser>'

def test_invalid_email():
    """Test that invalid emails are not accepted."""
    with pytest.raises(ValueError):
        User(
            username='testuser',
            email='invalid-email',
            password='testpass123'
        )

def test_password_hashing():
    """Test password hashing works correctly."""
    user = User(
        username='testuser',
        email='test@test.com',
        password='testpass123'
    )
    
    assert user.password_hash is not None
    assert user.check_password('testpass123')
    assert not user.check_password('wrongpass') 