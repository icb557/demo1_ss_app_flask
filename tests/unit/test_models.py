"""Unit tests for models."""
import pytest
from datetime import datetime
from app.models import User, Task, TravelDiary, Activity

def test_new_user():
    """Test creating a new user."""
    user = User(username='test_user', email='test@example.com')
    assert user.username == 'test_user'
    assert user.email == 'test@example.com'
    assert isinstance(user.created_at, datetime)

def test_new_task():
    """Test creating a new task."""
    user = User(username='test_user', email='test@example.com')
    task = Task(
        title='Test Task',
        description='Test Description',
        due_date=datetime.utcnow(),
        category='personal',
        status='pending',
        user=user
    )
    assert task.title == 'Test Task'
    assert task.description == 'Test Description'
    assert isinstance(task.due_date, datetime)
    assert task.category == 'personal'
    assert task.status == 'pending'
    assert task.user == user

def test_task_status_transition():
    """Test task status transitions."""
    task = Task(title='Test Task', status='pending')
    task.mark_completed()
    assert task.status == 'completed'
    assert isinstance(task.completed_at, datetime)

def test_new_travel_diary():
    """Test creating a new travel diary entry."""
    user = User(username='test_user', email='test@example.com')
    diary = TravelDiary(
        title='Trip to Barcelona',
        location='Barcelona, Spain',
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow(),
        description='Amazing trip to Barcelona',
        user=user
    )
    assert diary.title == 'Trip to Barcelona'
    assert diary.location == 'Barcelona, Spain'
    assert isinstance(diary.start_date, datetime)
    assert isinstance(diary.end_date, datetime)
    assert diary.description == 'Amazing trip to Barcelona'
    assert diary.user == user

def test_add_activity_to_diary():
    """Test adding an activity to a travel diary."""
    diary = TravelDiary(title='Trip to Barcelona')
    activity = Activity(
        title='Visit Sagrada Familia',
        description='Visit the famous church',
        planned_date=datetime.utcnow(),
        diary=diary
    )
    assert activity in diary.activities
    assert activity.title == 'Visit Sagrada Familia'
    assert activity.diary == diary

def test_activity_completion():
    """Test marking an activity as completed."""
    activity = Activity(title='Visit Sagrada Familia')
    activity.mark_completed()
    assert activity.is_completed
    assert isinstance(activity.completed_at, datetime)

def test_diary_to_dict():
    """Test travel diary to dictionary conversion."""
    diary = TravelDiary(
        title='Trip to Barcelona',
        location='Barcelona, Spain',
        description='Amazing trip'
    )
    activity = Activity(
        title='Visit Sagrada Familia',
        description='Visit the church',
        diary=diary
    )
    diary_dict = diary.to_dict()
    assert diary_dict['title'] == 'Trip to Barcelona'
    assert diary_dict['location'] == 'Barcelona, Spain'
    assert len(diary_dict['activities']) == 1
    assert diary_dict['activities'][0]['title'] == 'Visit Sagrada Familia'

def test_user_repr():
    """Test user string representation."""
    user = User(username='test_user', email='test@example.com')
    assert str(user) == '<User test_user>'

def test_user_to_dict():
    """Test user to dictionary conversion."""
    user = User(username='test_user', email='test@example.com')
    user_dict = user.to_dict()
    assert user_dict['username'] == 'test_user'
    assert user_dict['email'] == 'test@example.com'
    assert isinstance(user_dict['created_at'], str) 