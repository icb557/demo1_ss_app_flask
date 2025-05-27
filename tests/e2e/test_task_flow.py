"""End-to-end tests for the task management feature."""
import pytest
from datetime import datetime, timedelta
from flask import url_for
from flask_login import current_user
from app.models import User, Task
from app import db

def test_task_flow(client, test_user, init_database):
    """Test the complete task management flow."""
    # Login
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Create a new task
    task_data = {
        'title': 'Test Task',
        'description': 'Test Description',
        'category': 'personal',
        'due_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    }
    response = client.post('/tasks', data=task_data, follow_redirects=True)
    assert response.status_code == 200
    assert 'Test Task' in response.get_data(as_text=True)
    
    # Get the created task
    task = Task.query.filter_by(title='Test Task').first()
    assert task is not None
    
    # View task details
    response = client.get(f'/tasks/{task.id}')
    assert response.status_code == 200
    assert 'Test Task' in response.get_data(as_text=True)
    
    # Update the task
    update_data = {
        'title': 'Updated Task',
        'description': 'Updated Description',
        'category': 'work',
        'due_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    }
    response = client.post(f'/tasks/{task.id}', data=update_data, follow_redirects=True)
    assert response.status_code == 200
    assert 'Updated Task' in response.get_data(as_text=True)
    
    # Complete the task
    response = client.post(f'/tasks/{task.id}/complete', follow_redirects=True)
    assert response.status_code == 200
    assert 'Tarea completada exitosamente' in response.get_data(as_text=True)
    
    # Filter tasks
    response = client.get('/tasks?category=work&status=completed')
    assert response.status_code == 200
    assert 'Updated Task' in response.get_data(as_text=True)
    
    # Delete the task
    response = client.delete(f'/tasks/{task.id}')
    assert response.status_code == 200
    assert 'Tarea eliminada exitosamente' in response.get_data(as_text=True) 