"""End-to-end tests for the web views."""
import pytest
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def test_index_page(client):
    """Test the index page shows both tasks and diary sections."""
    response = client.get('/')
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Verify main sections exist
    assert soup.find(id='tasks-section')
    assert soup.find(id='diary-section')

def test_create_task_flow(client, test_user):
    """Test creating a task through the web interface."""
    # Get the create task form
    response = client.get('/tasks/create')
    assert response.status_code == 200
    
    # Submit the form
    response = client.post('/tasks/create', data={
        'title': 'Test Task',
        'description': 'Task created via web form',
        'due_date': (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d'),
        'category': 'work'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Verify task appears in the task list
    task_list = soup.find(id='task-list')
    task_items = task_list.find_all('div', class_='task-item')
    assert any(task.find('h3').text == 'Test Task' for task in task_items)

def test_create_travel_diary_flow(client, test_user):
    """Test creating a travel diary through the web interface."""
    # Get the create diary form
    response = client.get('/diary/create')
    assert response.status_code == 200
    
    # Submit the form
    response = client.post('/diary/create', data={
        'title': 'Barcelona Trip',
        'location': 'Barcelona, Spain',
        'start_date': datetime.utcnow().strftime('%Y-%m-%d'),
        'end_date': (datetime.utcnow() + timedelta(days=5)).strftime('%Y-%m-%d'),
        'description': 'Amazing trip planned'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Verify diary appears in the diary list
    diary_list = soup.find(id='diary-list')
    diary_items = diary_list.find_all('div', class_='diary-item')
    assert any(diary.find('h3').text == 'Barcelona Trip' for diary in diary_items)

def test_add_activity_to_diary_flow(client, test_user):
    """Test adding an activity to a diary through the web interface."""
    # First create a diary
    response = client.post('/diary/create', data={
        'title': 'Paris Trip',
        'location': 'Paris, France'
    }, follow_redirects=True)
    
    soup = BeautifulSoup(response.data, 'html.parser')
    diary_id = soup.find('div', class_='diary-item')['data-diary-id']
    
    # Add activity to the diary
    response = client.post(f'/diary/{diary_id}/activity/add', data={
        'title': 'Visit Eiffel Tower',
        'description': 'Evening visit',
        'planned_date': (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d')
    }, follow_redirects=True)
    
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Verify activity appears in the diary's activity list
    activities = soup.find_all('div', class_='activity-item')
    assert any(act.find('h4').text == 'Visit Eiffel Tower' for act in activities)

def test_mark_task_completed_flow(client, test_user):
    """Test marking a task as completed through the web interface."""
    # Create a task
    response = client.post('/tasks/create', data={
        'title': 'Task to Complete',
        'due_date': datetime.utcnow().strftime('%Y-%m-%d')
    }, follow_redirects=True)
    
    soup = BeautifulSoup(response.data, 'html.parser')
    task_id = soup.find('div', class_='task-item')['data-task-id']
    
    # Mark task as completed
    response = client.post(f'/tasks/{task_id}/complete', follow_redirects=True)
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    completed_task = soup.find('div', {'data-task-id': task_id})
    assert 'completed' in completed_task['class']

def test_search_functionality(client, test_user):
    """Test search functionality in the web interface."""
    # Create some test data
    client.post('/tasks/create', data={
        'title': 'Work Presentation',
        'category': 'work'
    }, follow_redirects=True)
    
    client.post('/diary/create', data={
        'title': 'Spain Vacation',
        'location': 'Barcelona, Spain'
    }, follow_redirects=True)
    
    # Test search in tasks
    response = client.get('/search?q=work&type=tasks')
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    results = soup.find_all('div', class_='search-result')
    assert any('Work Presentation' in res.text for res in results)
    
    # Test search in diaries
    response = client.get('/search?q=spain&type=diaries')
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    results = soup.find_all('div', class_='search-result')
    assert any('Spain Vacation' in res.text for res in results)

def test_dashboard_view(client, test_user):
    """Test the dashboard view showing combined tasks and diary information."""
    response = client.get('/dashboard')
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Verify dashboard sections
    assert soup.find(id='upcoming-tasks')
    assert soup.find(id='upcoming-trips')
    assert soup.find(id='recent-activities')
    
    # Verify task filters
    filters = soup.find(id='task-filters')
    assert filters.find('option', value='all')
    assert filters.find('option', value='pending')
    assert filters.find('option', value='completed') 