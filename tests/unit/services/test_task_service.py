"""Unit tests for TaskService."""
import pytest
from datetime import datetime, timezone
from app.models import User, Task
from app.services.task_service import TaskService
from app import db

class TestTaskService:
    """Test cases for TaskService."""

    def test_create_task(self):
        """Test task creation."""
        user = User(username='test_user', email='test@example.com')
        task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': datetime.now(timezone.utc),
            'category': 'personal',
            'status': 'pending'
        }
        
        task_service = TaskService()
        task = task_service.create_task(user, **task_data)
        
        assert task.title == task_data['title']
        assert task.user == user
        assert task.status == 'pending'

    def test_get_user_tasks(self):
        """Test getting all tasks for a user."""
        user = User(username='test_user', email='test@example.com')
        task_service = TaskService()
        
        task1 = Task(title='Task 1', user=user)
        task2 = Task(title='Task 2', user=user)
        db.session.add_all([task1, task2])
        db.session.commit()

        user_tasks = task_service.get_user_tasks(user)
        assert len(user_tasks) == 2
        assert all(task.user == user for task in user_tasks)

    def test_mark_task_completed(self):
        """Test marking a task as completed."""
        task_service = TaskService()
        task = Task(title='Test Task', status='pending')
        
        updated_task = task_service.mark_task_completed(task)
        assert updated_task.status == 'completed'
        assert updated_task.completed_at is not None 