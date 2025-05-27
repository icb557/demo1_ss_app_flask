"""End-to-end tests for the authentication feature."""
import pytest
from flask import url_for
from app.models import User
from app import db

def test_auth_flow(client, init_database):
    """Test the complete authentication flow."""
    # Register a new user
    register_data = {
        'username': 'new_user',
        'email': 'new@example.com',
        'password': 'password123',
        'password_confirm': 'password123'
    }
    response = client.post('/auth/register', data=register_data, follow_redirects=True)
    assert response.status_code == 200
    assert '¡Registro exitoso!' in response.get_data(as_text=True)
    
    # Try to register with same email
    response = client.post('/auth/register', data=register_data, follow_redirects=True)
    assert response.status_code == 200
    assert 'Username already exists' in response.get_data(as_text=True)
    
    # Login with wrong password
    login_data = {
        'email': 'new@example.com',
        'password': 'wrongpassword'
    }
    response = client.post('/auth/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    assert 'Email o contraseña incorrectos' in response.get_data(as_text=True)
    
    # Login with correct password
    login_data['password'] = 'password123'
    response = client.post('/auth/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    assert '¡Bienvenido!' in response.get_data(as_text=True)
    
    # Access protected route
    response = client.get('/profile')
    assert response.status_code == 200
    assert 'new_user' in response.get_data(as_text=True)
    
    # Logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert 'Has cerrado sesión exitosamente' in response.get_data(as_text=True)
    
    # Try to access protected route after logout
    response = client.get('/profile')
    assert response.status_code == 302  # Redirect to login 