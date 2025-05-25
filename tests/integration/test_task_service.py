"""Integration tests for task service."""
import pytest
from datetime import datetime, timedelta
from app.services import TaskService
from app.models import Task

def test_create_task(app, test_user):
    """Test task creation."""
    with app.app_context():
        task = TaskService.create_task(
            user=test_user,
            title='Test Task',
            description='Test Description',
            due_date=datetime.utcnow() + timedelta(days=1),
            category='personal'
        )
        assert task.title == 'Test Task'
        assert task.user == test_user
        
        # Verify task was saved to database
        saved_task = Task.query.filter_by(title='Test Task').first()
        assert saved_task is not None
        assert saved_task.description == 'Test Description'

def test_get_user_tasks_for_view(app, test_user):
    """Test getting user's tasks for view rendering."""
    with app.app_context():
        # Create multiple tasks
        TaskService.create_task(test_user, 'Task 1', category='work')
        TaskService.create_task(test_user, 'Task 2', category='personal')
        
        # Get tasks for different views
        dashboard_tasks = TaskService.get_tasks_for_dashboard(test_user)
        assert len(dashboard_tasks['upcoming']) > 0
        assert len(dashboard_tasks['pending']) > 0
        
        # Get tasks by category for view
        work_tasks = TaskService.get_tasks_by_category(test_user, 'work')
        assert len(work_tasks) == 1
        assert work_tasks[0].title == 'Task 1'
        
        # Get tasks with pagination for list view
        page_tasks = TaskService.get_paginated_tasks(test_user, page=1, per_page=10)
        assert len(page_tasks.items) == 2
        assert page_tasks.total == 2

def test_mark_task_completed(app, test_user):
    """Test marking task as completed."""
    with app.app_context():
        task = TaskService.create_task(test_user, 'Test Task')
        
        # Mark as completed
        updated_task = TaskService.mark_task_completed(task)
        assert updated_task.status == 'completed'
        assert isinstance(updated_task.completed_at, datetime)
        
        # Verify in database and get updated view data
        task_data = TaskService.get_task_with_related_data(task.id)
        assert task_data['task'].status == 'completed'
        assert 'related_diary' in task_data

def test_get_tasks_by_filter(app, test_user):
    """Test getting tasks by different filters for views."""
    with app.app_context():
        today = datetime.utcnow()
        tomorrow = today + timedelta(days=1)
        
        # Create tasks with different dates and statuses
        task1 = TaskService.create_task(test_user, 'Today Task', due_date=today)
        task2 = TaskService.create_task(test_user, 'Tomorrow Task', due_date=tomorrow)
        TaskService.mark_task_completed(task1)
        
        # Test different view filters
        completed = TaskService.get_filtered_tasks(test_user, status='completed')
        assert len(completed) == 1
        assert completed[0].title == 'Today Task'
        
        upcoming = TaskService.get_filtered_tasks(test_user, due_after=today)
        assert len(upcoming) == 1
        assert upcoming[0].title == 'Tomorrow Task'

def test_task_summary_data(app, test_user):
    """Test getting task summary data for dashboard."""
    with app.app_context():
        # Create tasks with different statuses
        TaskService.create_task(test_user, 'Task 1', category='work')
        task2 = TaskService.create_task(test_user, 'Task 2', category='personal')
        TaskService.mark_task_completed(task2)
        
        summary = TaskService.get_task_summary(test_user)
        assert summary['total_tasks'] == 2
        assert summary['completed_tasks'] == 1
        assert summary['pending_tasks'] == 1
        assert 'work' in summary['tasks_by_category']
        assert 'personal' in summary['tasks_by_category'] 