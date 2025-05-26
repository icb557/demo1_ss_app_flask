"""Integration tests for User and Task models."""
import pytest
from datetime import datetime, timezone, timedelta
from app.models import User, Task
from app import db

def test_user_task_relationship(init_database, app):
    """Test the relationship between User and Task models."""
    with app.app_context():
        # Create a test user
        user = User(
            username='integration_test_user',
            email='integration@test.com'
        )
        db.session.add(user)
        db.session.commit()

        # Create tasks for the user
        task1 = Task(
            title='Test Task 1',
            description='Description for test task 1',
            due_date=datetime.now(timezone.utc) + timedelta(days=1),
            status='pending',
            user=user
        )
        task2 = Task(
            title='Test Task 2',
            description='Description for test task 2',
            due_date=datetime.now(timezone.utc) + timedelta(days=2),
            status='pending',
            user=user
        )

        db.session.add_all([task1, task2])
        db.session.commit()

        # Test relationships
        assert len(user.tasks) == 2
        assert user.tasks[0].title == 'Test Task 1'
        assert user.tasks[1].title == 'Test Task 2'
        assert task1.user == user
        assert task2.user == user

def test_task_crud_operations(init_database, app):
    """Test CRUD operations for Task model."""
    with app.app_context():
        # Create a test user
        user = User(
            username='crud_test_user',
            email='crud@test.com'
        )
        db.session.add(user)
        db.session.commit()

        # Create a task
        task = Task(
            title='CRUD Test Task',
            description='Testing CRUD operations',
            due_date=datetime.now(timezone.utc) + timedelta(days=1),
            status='pending',
            user=user
        )
        db.session.add(task)
        db.session.commit()

        # Read
        retrieved_task = Task.query.filter_by(title='CRUD Test Task').first()
        assert retrieved_task is not None
        assert retrieved_task.description == 'Testing CRUD operations'

        # Update
        retrieved_task.status = 'completed'
        db.session.commit()
        updated_task = db.session.get(Task, retrieved_task.id)
        assert updated_task.status == 'completed'

        # Delete
        db.session.delete(retrieved_task)
        db.session.commit()
        deleted_task = db.session.get(Task, retrieved_task.id)
        assert deleted_task is None

def test_cascade_delete(init_database, app):
    """Test cascade delete between User and Task."""
    with app.app_context():
        # Create a test user
        user = User(
            username='cascade_test_user',
            email='cascade@test.com'
        )
        db.session.add(user)
        db.session.commit()

        # Create tasks for the user
        tasks = [
            Task(
                title=f'Cascade Task {i}',
                description=f'Description for cascade task {i}',
                due_date=datetime.now(timezone.utc) + timedelta(days=i),
                status='pending',
                user=user
            )
            for i in range(3)
        ]
        db.session.add_all(tasks)
        db.session.commit()

        # Verify tasks were created
        assert Task.query.filter_by(user_id=user.id).count() == 3

        # Delete user and verify cascade
        db.session.delete(user)
        db.session.commit()

        # Verify all related tasks were deleted
        assert Task.query.filter_by(user_id=user.id).count() == 0 