"""Unit tests for TaskService."""
import pytest
from datetime import datetime, timezone
from app.models import User, Task
from app.services.task_service import TaskService
from app import db

@pytest.fixture
def task_service():
    """Fixture for TaskService."""
    return TaskService()

@pytest.fixture
def sample_task_data():
    """Fixture for sample task data."""
    return {
        'title': 'Test Task',
        'description': 'Test Description',
        'due_date': datetime.now(timezone.utc),
        'category': 'personal',
        'status': 'pending'
    }

class TestTaskService:
    """Test cases for TaskService."""

    def test_create_task_success(self, init_database, task_service, test_user, sample_task_data):
        """Test successful task creation."""
        task = task_service.create_task(test_user, **sample_task_data)
        
        assert task.title == sample_task_data['title']
        assert task.description == sample_task_data['description']
        assert isinstance(task.due_date, datetime)
        assert task.category == sample_task_data['category']
        assert task.status == 'pending'
        assert task.user == test_user
        assert isinstance(task.created_at, datetime)

    def test_create_task_invalid_category(self, init_database, task_service, test_user):
        """Test task creation with invalid category."""
        invalid_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': datetime.now(timezone.utc),
            'category': 'invalid_category',
            'status': 'pending'
        }
        
        with pytest.raises(ValueError) as exc_info:
            task_service.create_task(test_user, **invalid_data)
        assert str(exc_info.value) == "Invalid category"

    def test_create_task_invalid_status(self, init_database, task_service, test_user):
        """Test task creation with invalid status."""
        invalid_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': datetime.now(timezone.utc),
            'category': 'personal',
            'status': 'invalid_status'
        }
        
        with pytest.raises(ValueError) as exc_info:
            task_service.create_task(test_user, **invalid_data)
        assert str(exc_info.value) == "Invalid status"

    def test_get_task_by_id_success(self, init_database, task_service, test_user, sample_task_data):
        """Test successfully getting task by ID."""
        task = task_service.create_task(test_user, **sample_task_data)
        db.session.add(task)
        db.session.commit()

        retrieved_task = task_service.get_task_by_id(task.id)
        assert retrieved_task == task
        assert retrieved_task.title == sample_task_data['title']

    def test_get_task_by_id_not_found(self, init_database, task_service):
        """Test getting non-existent task by ID."""
        with pytest.raises(ValueError) as exc_info:
            task_service.get_task_by_id(999)
        assert str(exc_info.value) == "Task not found"

    def test_get_user_tasks(self, init_database, task_service, test_user):
        """Test getting all tasks for a user."""
        # Create multiple tasks
        task1_data = {'title': 'Task 1', 'description': 'First task', 'category': 'personal', 'status': 'pending'}
        task2_data = {'title': 'Task 2', 'description': 'Second task', 'category': 'work', 'status': 'pending'}
        
        task1 = task_service.create_task(test_user, **task1_data)
        task2 = task_service.create_task(test_user, **task2_data)
        
        db.session.add_all([task1, task2])
        db.session.commit()

        # Get tasks
        tasks = task_service.get_user_tasks(test_user)
        assert len(tasks) == 2
        assert all(task.user == test_user for task in tasks)

    def test_get_user_tasks_by_category(self, init_database, task_service, test_user):
        """Test getting user tasks filtered by category."""
        # Create tasks with different categories
        personal_task = task_service.create_task(test_user, title='Personal Task', category='personal', status='pending')
        work_task = task_service.create_task(test_user, title='Work Task', category='work', status='pending')
        
        db.session.add_all([personal_task, work_task])
        db.session.commit()

        # Get tasks filtered by category
        personal_tasks = task_service.get_user_tasks(test_user, category='personal')
        assert len(personal_tasks) == 1
        assert all(task.category == 'personal' for task in personal_tasks)

    def test_get_user_tasks_by_status(self, init_database, task_service, test_user):
        """Test getting user tasks filtered by status."""
        # Create tasks with different statuses
        pending_task = task_service.create_task(test_user, title='Pending Task', category='personal', status='pending')
        completed_task = task_service.create_task(test_user, title='Completed Task', category='personal', status='completed')
        
        db.session.add_all([pending_task, completed_task])
        db.session.commit()

        # Get tasks filtered by status
        pending_tasks = task_service.get_user_tasks(test_user, status='pending')
        assert len(pending_tasks) == 1
        assert all(task.status == 'pending' for task in pending_tasks)

    def test_update_task_success(self, init_database, task_service, test_user, sample_task_data):
        """Test successful task update."""
        task = task_service.create_task(test_user, **sample_task_data)
        db.session.add(task)
        db.session.commit()
        
        update_data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'category': 'work'
        }
        updated_task = task_service.update_task(task, update_data)
        
        assert updated_task.title == update_data['title']
        assert updated_task.description == update_data['description']
        assert updated_task.category == update_data['category']
        assert updated_task.updated_at > updated_task.created_at

    def test_update_task_invalid_category(self, init_database, task_service, test_user, sample_task_data):
        """Test updating task with invalid category."""
        task = task_service.create_task(test_user, **sample_task_data)
        db.session.add(task)
        db.session.commit()
        
        with pytest.raises(ValueError) as exc_info:
            task_service.update_task(task, {'category': 'invalid_category'})
        assert str(exc_info.value) == "Invalid category"

    def test_mark_task_completed(self, init_database, task_service, test_user, sample_task_data):
        """Test marking a task as completed."""
        task = task_service.create_task(test_user, **sample_task_data)
        db.session.add(task)
        db.session.commit()
        
        completed_task = task_service.mark_task_completed(task)
        assert completed_task.status == 'completed'
        assert isinstance(completed_task.completed_at, datetime)

    def test_delete_task(self, init_database, task_service, test_user, sample_task_data):
        """Test task deletion."""
        task = task_service.create_task(test_user, **sample_task_data)
        db.session.add(task)
        db.session.commit()
        
        task_service.delete_task(task)
        
        with pytest.raises(ValueError):
            task_service.get_task_by_id(task.id) 