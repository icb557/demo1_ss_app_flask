"""Test cases for Task model."""
import pytest
from datetime import datetime, timedelta, timezone
from app.models import Task, User
from app import db

def test_new_task(test_user, init_database, app):
    """Test creating a new task."""
    with app.app_context():
        task = Task(
            title='Test Task',
            description='Test Description',
            due_date=datetime.now(timezone.utc),
            category='personal',
            status='pending',
            user=test_user
        )
        db.session.add(task)
        db.session.commit()

        assert task.title == 'Test Task'
        assert task.description == 'Test Description'
        assert isinstance(task.due_date, datetime)
        assert task.category == 'personal'
        assert task.status == 'pending'
        assert task.user == test_user
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

def test_task_status_transition(init_database, app):
    """Test task status transitions."""
    with app.app_context():
        task = Task(title='Test Task', status='pending')
        db.session.add(task)
        db.session.commit()
        
        task.mark_completed()
        db.session.commit()
        
        assert task.status == 'completed'
        assert isinstance(task.completed_at, datetime)

def test_task_representation():
    """Test string representation of task."""
    task = Task(title='Test Task')
    assert str(task) == '<Task: Test Task>'

def test_invalid_category():
    """Test that invalid category values are not accepted."""
    with pytest.raises(ValueError):
        Task(
            title='Test Task',
            category='invalid_category'
        )

def test_invalid_status():
    """Test that invalid status values are not accepted."""
    with pytest.raises(ValueError):
        Task(
            title='Test Task',
            status='invalid_status'
        )

def test_task_is_overdue(init_database, app):
    """Test overdue task detection."""
    with app.app_context():
        # Create a task due yesterday
        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        task = Task(
            title='Test Task',
            due_date=past_date
        )
        db.session.add(task)
        db.session.commit()
        assert task.is_overdue()

        # Create a task due tomorrow
        future_date = datetime.now(timezone.utc) + timedelta(days=1)
        task = Task(
            title='Test Task',
            due_date=future_date
        )
        db.session.add(task)
        db.session.commit()
        assert not task.is_overdue()

def test_task_priority():
    """Test task priority assignment and validation."""
    task = Task(
        title='Test Task',
        priority='high'
    )
    assert task.priority == 'high'

    with pytest.raises(ValueError):
        Task(
            title='Test Task',
            priority='invalid_priority'
        )

def test_default_values():
    """Test default values for task fields."""
    task = Task(title='Test Task')
    assert task.status == 'pending'
    assert task.priority == 'medium'
    assert task.category == 'general'
    assert task.description == ''
    assert task.completed_at is None

def test_task_completion_with_notes(init_database, app):
    """Test completing a task with completion notes."""
    with app.app_context():
        task = Task(title='Test Task')
        db.session.add(task)
        db.session.commit()
        
        completion_note = 'Completed with some observations'
        task.mark_completed(completion_note)
        db.session.commit()
        
        assert task.status == 'completed'
        assert task.completion_notes == completion_note
        assert isinstance(task.completed_at, datetime)

def test_required_fields():
    """Test that required fields are enforced."""
    with pytest.raises(ValueError):
        Task()  # Missing title

def test_task_user_relationship(test_user, init_database, app):
    """Test task-user relationship."""
    with app.app_context():
        task = Task(
            title='Test Task',
            user=test_user
        )
        db.session.add(task)
        db.session.commit()
        
        assert task in test_user.tasks
        assert task.user.username == test_user.username 