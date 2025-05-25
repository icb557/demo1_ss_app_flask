"""Integration tests for user service."""
import pytest
from datetime import datetime, timedelta
from app.services import UserService
from app.models import User, Session
from flask_login import current_user
from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError

def test_create_user(app):
    """Test user creation with password hashing."""
    with app.app_context():
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='secure_password'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert check_password_hash(user.password_hash, 'secure_password')
        
        # Verify user was saved to database
        saved_user = User.query.filter_by(email='test@example.com').first()
        assert saved_user is not None
        assert saved_user.username == 'testuser'

def test_user_authentication(app):
    """Test user authentication and session management."""
    with app.app_context():
        # Create test user
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='secure_password'
        )
        
        # Test successful authentication
        auth_user = UserService.authenticate_user('test@example.com', 'secure_password')
        assert auth_user is not None
        assert auth_user.id == user.id
        
        # Test failed authentication
        assert UserService.authenticate_user('test@example.com', 'wrong_password') is None
        assert UserService.authenticate_user('wrong@email.com', 'secure_password') is None

def test_session_management(app, test_client):
    """Test session creation and management."""
    with app.app_context():
        # Create and login user
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='secure_password'
        )
        
        session = UserService.create_session(user)
        assert session.user_id == user.id
        assert session.is_active
        
        # Test session validation
        assert UserService.validate_session(session.id)
        
        # Test session expiry
        expired_session = UserService.create_session(
            user,
            expiry=datetime.utcnow() - timedelta(days=1)
        )
        assert not UserService.validate_session(expired_session.id)

def test_remember_me_token(app):
    """Test remember me token functionality."""
    with app.app_context():
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='secure_password'
        )
        
        # Generate remember token
        token = UserService.generate_remember_token(user)
        assert token is not None
        
        # Verify token
        verified_user = UserService.verify_remember_token(token)
        assert verified_user is not None
        assert verified_user.id == user.id
        
        # Test invalid token
        assert UserService.verify_remember_token('invalid_token') is None

def test_password_reset(app):
    """Test password reset functionality."""
    with app.app_context():
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='original_password'
        )
        
        # Generate reset token
        token = UserService.generate_password_reset_token(user)
        assert token is not None
        
        # Reset password
        new_password = 'new_secure_password'
        success = UserService.reset_password(token, new_password)
        assert success
        
        # Verify new password works
        updated_user = UserService.authenticate_user('test@example.com', new_password)
        assert updated_user is not None
        assert updated_user.id == user.id

def test_user_profile_management(app):
    """Test user profile management."""
    with app.app_context():
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='secure_password'
        )
        
        # Update profile
        updated_user = UserService.update_profile(
            user,
            new_username='updated_user',
            new_email='updated@example.com'
        )
        assert updated_user.username == 'updated_user'
        assert updated_user.email == 'updated@example.com'
        
        # Verify changes in database
        saved_user = User.query.get(user.id)
        assert saved_user.username == 'updated_user'
        assert saved_user.email == 'updated@example.com'

def test_session_cleanup(app):
    """Test automatic cleanup of expired sessions."""
    with app.app_context():
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='secure_password'
        )
        
        # Create multiple sessions
        active_session = UserService.create_session(user)
        expired_session = UserService.create_session(
            user,
            expiry=datetime.utcnow() - timedelta(days=1)
        )
        
        # Run cleanup
        cleaned = UserService.cleanup_expired_sessions()
        assert cleaned > 0
        
        # Verify only expired sessions were removed
        assert UserService.validate_session(active_session.id)
        assert not UserService.validate_session(expired_session.id)

def test_concurrent_sessions_limit(app):
    """Test limiting number of concurrent sessions per user."""
    with app.app_context():
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='secure_password'
        )
        
        # Create maximum allowed sessions
        max_sessions = 3
        sessions = []
        for _ in range(max_sessions):
            session = UserService.create_session(user)
            sessions.append(session)
            assert session is not None
        
        # Try to create one more session
        overflow_session = UserService.create_session(user)
        assert overflow_session is not None
        
        # Verify oldest session was invalidated
        assert not UserService.validate_session(sessions[0].id)
        assert all(UserService.validate_session(s.id) for s in sessions[1:])

def test_get_user_by_id(app, test_user):
    """Test getting user by ID."""
    with app.app_context():
        user = UserService.get_user_by_id(test_user.id)
        assert user is not None
        assert user.username == test_user.username

def test_get_user_by_username(app, test_user):
    """Test getting user by username."""
    with app.app_context():
        user = UserService.get_user_by_username(test_user.username)
        assert user is not None
        assert user.id == test_user.id

def test_get_all_users(app, test_user):
    """Test getting all users."""
    with app.app_context():
        # Create another user
        UserService.create_user('another_user', 'another@example.com')
        
        users = UserService.get_all_users()
        assert len(users) == 2
        assert any(u.username == test_user.username for u in users)
        assert any(u.username == 'another_user' for u in users)

def test_update_user(app, test_user):
    """Test updating user information."""
    with app.app_context():
        updated_user = UserService.update_user(
            test_user,
            username='updated_user',
            email='updated@example.com'
        )
        assert updated_user.username == 'updated_user'
        assert updated_user.email == 'updated@example.com'
        
        # Verify changes were saved to database
        saved_user = User.query.get(test_user.id)
        assert saved_user.username == 'updated_user'
        assert saved_user.email == 'updated@example.com'

def test_delete_user(app, test_user):
    """Test user deletion."""
    with app.app_context():
        UserService.delete_user(test_user)
        
        # Verify user was deleted from database
        deleted_user = User.query.get(test_user.id)
        assert deleted_user is None

def test_password_validation(app):
    """Test password validation rules."""
    with app.app_context():
        # Test password too short
        with pytest.raises(ValueError, match='Password must be at least 8 characters'):
            UserService.create_user(
                username='testuser',
                email='test@example.com',
                password='short'
            )
        
        # Test password without numbers
        with pytest.raises(ValueError, match='Password must contain at least one number'):
            UserService.create_user(
                username='testuser',
                email='test@example.com',
                password='onlyletters'
            )
        
        # Test password without special characters
        with pytest.raises(ValueError, match='Password must contain at least one special character'):
            UserService.create_user(
                username='testuser',
                email='test@example.com',
                password='nospecial123'
            )

def test_duplicate_user_prevention(app):
    """Test prevention of duplicate usernames and emails."""
    with app.app_context():
        # Create initial user
        UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='secure_password123!'
        )
        
        # Try creating user with same username
        with pytest.raises(IntegrityError):
            UserService.create_user(
                username='testuser',
                email='different@example.com',
                password='secure_password123!'
            )
        
        # Try creating user with same email
        with pytest.raises(IntegrityError):
            UserService.create_user(
                username='different_user',
                email='test@example.com',
                password='secure_password123!'
            )

def test_session_token_security(app):
    """Test session token security features."""
    with app.app_context():
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='secure_password123!'
        )
        
        # Test token length and complexity
        token = UserService.generate_session_token()
        assert len(token) >= 32
        assert any(c.isdigit() for c in token)
        assert any(c.isalpha() for c in token)
        
        # Test token expiration
        session = UserService.create_session(
            user,
            token=token,
            expiry=datetime.utcnow() + timedelta(minutes=30)
        )
        assert UserService.validate_session(session.id)
        
        # Simulate time passing
        session.expiry = datetime.utcnow() - timedelta(minutes=1)
        assert not UserService.validate_session(session.id)

def test_rate_limiting(app):
    """Test rate limiting for authentication attempts."""
    with app.app_context():
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='secure_password123!'
        )
        
        # Try multiple failed authentications
        for _ in range(5):
            UserService.authenticate_user('test@example.com', 'wrong_password')
        
        # Next attempt should be blocked
        with pytest.raises(ValueError, match='Too many login attempts'):
            UserService.authenticate_user('test@example.com', 'secure_password123!')
        
        # Wait for cooldown (simulated)
        UserService.reset_login_attempts('test@example.com')
        
        # Should work after reset
        auth_user = UserService.authenticate_user('test@example.com', 'secure_password123!')
        assert auth_user is not None

def test_session_cleanup_policy(app):
    """Test session cleanup policies."""
    with app.app_context():
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='secure_password123!'
        )
        
        # Create sessions with different states
        active_session = UserService.create_session(user)
        expired_session = UserService.create_session(
            user,
            expiry=datetime.utcnow() - timedelta(days=1)
        )
        inactive_session = UserService.create_session(user)
        inactive_session.last_activity = datetime.utcnow() - timedelta(days=7)
        
        # Run cleanup with different policies
        cleaned = UserService.cleanup_sessions(
            expire_after_days=1,
            inactive_after_days=5
        )
        
        assert cleaned == 2  # Should remove expired and inactive sessions
        assert UserService.validate_session(active_session.id)
        assert not UserService.validate_session(expired_session.id)
        assert not UserService.validate_session(inactive_session.id)

def test_user_account_status(app):
    """Test user account status management."""
    with app.app_context():
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='secure_password123!'
        )
        
        # Test account deactivation
        UserService.deactivate_account(user.id)
        assert not user.is_active
        
        # Attempt login with inactive account
        auth_user = UserService.authenticate_user('test@example.com', 'secure_password123!')
        assert auth_user is None
        
        # Reactivate account
        UserService.activate_account(user.id)
        assert user.is_active
        
        # Should be able to login again
        auth_user = UserService.authenticate_user('test@example.com', 'secure_password123!')
        assert auth_user is not None

def test_password_history(app):
    """Test password history and reuse prevention."""
    with app.app_context():
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='secure_password123!'
        )
        
        # Try to reuse current password
        with pytest.raises(ValueError, match='Cannot reuse recent passwords'):
            UserService.update_password(user, 'secure_password123!')
        
        # Change password successfully
        UserService.update_password(user, 'newPassword456!')
        
        # Try to reuse old password
        with pytest.raises(ValueError, match='Cannot reuse recent passwords'):
            UserService.update_password(user, 'secure_password123!') 