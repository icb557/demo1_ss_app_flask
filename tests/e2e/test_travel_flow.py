"""End-to-end tests for the travel diary feature."""
import pytest
from datetime import datetime, timedelta
from flask import url_for
from flask_login import current_user
from app.models import User, TravelDiary, Activity
from app import db

def test_travel_flow(client, test_user, init_database):
    """Test the complete travel diary flow."""
    # Login
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Create a new travel diary
    travel_data = {
        'title': 'Test Travel',
        'location': 'Test Location',
        'description': 'Test Description',
        'start_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        'end_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    }
    response = client.post('/travel', data=travel_data, follow_redirects=True)
    assert response.status_code == 200
    assert 'Test Travel' in response.get_data(as_text=True)
    
    # Get the created travel diary
    travel = TravelDiary.query.filter_by(title='Test Travel').first()
    assert travel is not None
    
    # View travel details
    response = client.get(f'/travel/{travel.id}')
    assert response.status_code == 200
    assert 'Test Travel' in response.get_data(as_text=True)
    assert 'Test Location' in response.get_data(as_text=True)
    
    # Create an activity
    activity_data = {
        'title': 'Test Activity',
        'location': 'Activity Location',
        'description': 'Activity Description',
        'planned_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
        'planned_time': '10:00',
        'cost': '100.50',
        'notes': 'Activity Notes'
    }
    response = client.post(f'/travel/{travel.id}/activity', data=activity_data, follow_redirects=True)
    assert response.status_code == 200
    assert 'Test Activity' in response.get_data(as_text=True)
    
    # Get the created activity
    activity = Activity.query.filter_by(title='Test Activity').first()
    assert activity is not None
    
    # Complete the activity
    completion_data = {
        'completion_notes': 'Activity completed successfully'
    }
    response = client.post(f'/travel/activity/{activity.id}/complete', data=completion_data, follow_redirects=True)
    assert response.status_code == 200
    assert 'Actividad completada exitosamente' in response.get_data(as_text=True)
    
    # Delete the activity
    response = client.delete(f'/travel/activity/{activity.id}')
    assert response.status_code == 200
    assert 'Actividad eliminada exitosamente' in response.get_data(as_text=True)
    
    # Delete the travel diary
    response = client.delete(f'/travel/{travel.id}')
    assert response.status_code == 200
    assert 'Viaje eliminado exitosamente' in response.get_data(as_text=True) 