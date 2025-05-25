"""End-to-end tests for authentication and session management."""
import pytest
from bs4 import BeautifulSoup
from flask_login import current_user
from flask import session

def test_login_flow(client):
    """Test the complete login flow."""
    # Get login page
    response = client.get('/login')
    assert response.status_code == 200
    
    # Submit login form
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'test_password'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert session.get('_user_id') is not None  # Verificar que se creó la sesión
    assert current_user.is_authenticated
    
    # Verify redirect to dashboard
    soup = BeautifulSoup(response.data, 'html.parser')
    assert soup.find(id='dashboard')
    assert 'Welcome back' in response.data.decode()

def test_register_flow(client):
    """Test user registration flow."""
    # Get registration page
    response = client.get('/register')
    assert response.status_code == 200
    
    # Submit registration form
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'secure_password',
        'confirm_password': 'secure_password'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert session.get('_user_id') is not None  # Usuario automáticamente logueado
    assert current_user.is_authenticated
    assert 'Account created successfully' in response.data.decode()

def test_session_persistence(client):
    """Test that user session persists across requests."""
    # Login
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'test_password'
    })
    
    # Visit multiple pages and verify session persists
    pages = ['/', '/dashboard', '/tasks', '/diary']
    for page in pages:
        response = client.get(page)
        assert response.status_code == 200
        assert current_user.is_authenticated
        assert session.get('_user_id') is not None

def test_logout_flow(client):
    """Test logout functionality."""
    # First login
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'test_password'
    })
    
    # Then logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert session.get('_user_id') is None  # Sesión limpiada
    assert not current_user.is_authenticated
    
    # Verify redirect to login page
    soup = BeautifulSoup(response.data, 'html.parser')
    assert soup.find('form', {'action': '/login'})

def test_protected_routes(client):
    """Test that protected routes require authentication."""
    protected_routes = [
        '/dashboard',
        '/tasks/create',
        '/diary/create',
        '/profile'
    ]
    
    # Try accessing without login
    for route in protected_routes:
        response = client.get(route, follow_redirects=True)
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, 'html.parser')
        assert soup.find('form', {'action': '/login'})  # Redirige al login
        assert 'Please log in to access this page' in response.data.decode()

def test_remember_me_functionality(client):
    """Test 'remember me' login functionality."""
    # Login with remember me
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'test_password',
        'remember': True
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert session.get('_user_id') is not None
    assert session.get('remember') == 'set'  # o el nombre que uses para la cookie remember
    
    # Simulate session expiry but remember cookie still valid
    with client.session_transaction() as sess:
        sess.clear()
    
    # User should still be logged in on next request
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert current_user.is_authenticated

def test_session_expiry(client):
    """Test session expiry behavior."""
    # Login
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'test_password'
    })
    
    # Simulate session expiry
    with client.session_transaction() as sess:
        sess.clear()
    
    # Try accessing protected route
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert not current_user.is_authenticated
    soup = BeautifulSoup(response.data, 'html.parser')
    assert soup.find('form', {'action': '/login'})

def test_concurrent_sessions(client, app):
    """Test handling of concurrent sessions."""
    # Create two clients
    client2 = app.test_client()
    
    # Login with both clients
    for c in [client, client2]:
        c.post('/login', data={
            'email': 'test@example.com',
            'password': 'test_password'
        })
    
    # Verify both sessions are active
    for c in [client, client2]:
        response = c.get('/dashboard')
        assert response.status_code == 200
        assert current_user.is_authenticated
    
    # Logout one client
    client.get('/logout')
    
    # Other client should still be logged in
    response = client2.get('/dashboard')
    assert response.status_code == 200
    assert current_user.is_authenticated

def test_login_validation_errors(client):
    """Test login form validation errors."""
    # Test empty form
    response = client.post('/login', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert 'Email is required' in response.data.decode()
    
    # Test invalid email format
    response = client.post('/login', data={
        'email': 'invalid-email',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Invalid email address' in response.data.decode()
    
    # Test wrong credentials
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'wrong_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Invalid email or password' in response.data.decode()

def test_register_validation_errors(client):
    """Test registration form validation errors."""
    # Test password mismatch
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'different_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Passwords must match' in response.data.decode()
    
    # Test existing username
    client.post('/register', data={
        'username': 'existinguser',
        'email': 'user1@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    response = client.post('/register', data={
        'username': 'existinguser',
        'email': 'user2@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Username already exists' in response.data.decode()

def test_csrf_protection(client):
    """Test CSRF protection on forms."""
    # Try to submit without CSRF token
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'test_password'
    })
    assert response.status_code == 400
    assert 'CSRF token missing' in response.data.decode()

def test_brute_force_protection(client):
    """Test protection against brute force attacks."""
    # Try multiple failed logins
    for _ in range(5):
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'wrong_password'
        }, follow_redirects=True)
    
    # Next attempt should be blocked
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'wrong_password'
    }, follow_redirects=True)
    assert 'Too many login attempts' in response.data.decode()

def test_password_reset_flow(client):
    """Test complete password reset flow."""
    # Request password reset
    response = client.post('/password/reset/request', data={
        'email': 'test@example.com'
    }, follow_redirects=True)
    assert 'Password reset instructions sent' in response.data.decode()
    
    # Get reset token from email (simulated)
    # En una implementación real, necesitarías interceptar el email
    token = "simulated_reset_token"
    
    # Try invalid token
    response = client.post('/password/reset/invalid_token', data={
        'password': 'new_password',
        'confirm_password': 'new_password'
    }, follow_redirects=True)
    assert 'Invalid or expired reset token' in response.data.decode()
    
    # Use valid token
    response = client.post(f'/password/reset/{token}', data={
        'password': 'new_password',
        'confirm_password': 'new_password'
    }, follow_redirects=True)
    assert 'Password successfully reset' in response.data.decode()

def test_session_fixation_protection(client):
    """Test protection against session fixation attacks."""
    # Get initial session ID
    client.get('/')
    initial_session_id = session.get('_id')
    
    # Login
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'test_password'
    })
    
    # Session ID should be different after login
    assert session.get('_id') != initial_session_id

def test_inactive_user_login(client):
    """Test login attempt with inactive/disabled user account."""
    # Assuming we have a way to deactivate users
    response = client.post('/login', data={
        'email': 'inactive@example.com',
        'password': 'test_password'
    }, follow_redirects=True)
    assert 'Account is inactive' in response.data.decode() 