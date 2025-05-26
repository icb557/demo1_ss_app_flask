"""Integration tests for TaskService."""
import pytest
from datetime import datetime, timezone, timedelta
from app.services.task_service import TaskService
from app.services.user_service import UserService
from app.models import Task
from app import db

def test_create_task(init_database, app):
    """Test task creation with TaskService."""
    with app.app_context():
        # Create a test user first
        user_service = UserService()
        user = user_service.create_user(
            username='task_test_user',
            email='task_test@example.com',
            password='test_password'
        )
        
        service = TaskService()
        
        # Test successful creation
        task = service.create_task(
            user=user,
            title='Test Task',
            category='personal',
            description='Test description',
            due_date=datetime.now(timezone.utc) + timedelta(days=1)
        )
        
        assert task.title == 'Test Task'
        assert task.category == 'personal'
        assert task.status == 'pending'
        assert task.description == 'Test description'
        assert task.user == user
        
        # Test invalid category
        with pytest.raises(ValueError, match="Invalid category"):
            service.create_task(
                user=user,
                title='Invalid Category Task',
                category='invalid_category'
            )
        
        # Test invalid status
        with pytest.raises(ValueError, match="Invalid status"):
            service.create_task(
                user=user,
                title='Invalid Status Task',
                category='personal',
                status='invalid_status'
            )

def test_get_task_methods(init_database, app):
    """Test methods to retrieve tasks."""
    with app.app_context():
        # Create a test user
        user_service = UserService()
        user = user_service.create_user(
            username='get_tasks_user',
            email='get_tasks@example.com',
            password='test_password'
        )
        
        service = TaskService()
        
        # Create test tasks
        task1 = service.create_task(
            user=user,
            title='Personal Task',
            category='personal'
        )
        
        task2 = service.create_task(
            user=user,
            title='Work Task',
            category='work',
            status='completed'
        )
        
        # Test get by ID
        retrieved_task = service.get_task_by_id(task1.id)
        assert retrieved_task.id == task1.id
        assert retrieved_task.title == 'Personal Task'
        
        # Test get user tasks
        all_tasks = service.get_user_tasks(user)
        assert len(all_tasks) == 2
        
        # Test get tasks by category
        personal_tasks = service.get_user_tasks(user, category='personal')
        assert len(personal_tasks) == 1
        assert personal_tasks[0].category == 'personal'
        
        # Test get tasks by status
        completed_tasks = service.get_user_tasks(user, status='completed')
        assert len(completed_tasks) == 1
        assert completed_tasks[0].status == 'completed'
        
        # Test get tasks by category and status
        personal_pending_tasks = service.get_user_tasks(user, category='personal', status='pending')
        assert len(personal_pending_tasks) == 1
        assert personal_pending_tasks[0].category == 'personal'
        assert personal_pending_tasks[0].status == 'pending'
        
        # Test not found case
        with pytest.raises(ValueError, match="Task not found"):
            service.get_task_by_id(9999)

def test_update_task(init_database, app):
    """Test updating task information."""
    with app.app_context():
        # Create a test user
        user_service = UserService()
        user = user_service.create_user(
            username='update_tasks_user',
            email='update_tasks@example.com',
            password='test_password'
        )
        
        service = TaskService()
        
        # Create a test task
        task = service.create_task(
            user=user,
            title='Task to Update',
            category='personal',
            description='Original description'
        )
        
        # Test updating various fields
        updated_task = service.update_task(task, {
            'title': 'Updated Title',
            'description': 'Updated description',
            'category': 'work',
            'status': 'completed'
        })
        
        assert updated_task.title == 'Updated Title'
        assert updated_task.description == 'Updated description'
        assert updated_task.category == 'work'
        assert updated_task.status == 'completed'
        assert updated_task.completed_at is not None
        
        # Test invalid category
        with pytest.raises(ValueError, match="Invalid category"):
            service.update_task(task, {'category': 'invalid_category'})
        
        # Test invalid status
        with pytest.raises(ValueError, match="Invalid status"):
            service.update_task(task, {'status': 'invalid_status'})

def test_mark_task_completed(init_database, app):
    """Test marking a task as completed."""
    with app.app_context():
        # Create a test user
        user_service = UserService()
        user = user_service.create_user(
            username='complete_tasks_user',
            email='complete_tasks@example.com',
            password='test_password'
        )
        
        service = TaskService()
        
        # Create a test task
        task = service.create_task(
            user=user,
            title='Task to Complete',
            category='personal'
        )
        
        # Mark task as completed
        completed_task = service.mark_task_completed(task)
        assert completed_task.status == 'completed'
        assert completed_task.completed_at is not None

def test_delete_task(init_database, app):
    """Test task deletion."""
    with app.app_context():
        # Create a test user
        user_service = UserService()
        user = user_service.create_user(
            username='delete_tasks_user',
            email='delete_tasks@example.com',
            password='test_password'
        )
        
        service = TaskService()
        
        # Create a test task
        task = service.create_task(
            user=user,
            title='Task to Delete',
            category='personal'
        )
        
        # Delete the task
        service.delete_task(task)
        
        # Verify task is deleted
        with pytest.raises(ValueError, match="Task not found"):
            service.get_task_by_id(task.id) 