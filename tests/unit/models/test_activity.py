"""Test cases for Activity model."""
import pytest
from datetime import datetime, timezone, timedelta
from app.models import Activity, TravelDiary
from app import db

def test_new_activity(init_database, app):
    """Test creating a new activity."""
    with app.app_context():
        diary = TravelDiary(
            title='Trip to Barcelona',
            location='Barcelona, Spain',
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.session.add(diary)
        db.session.commit()

        activity = Activity(
            title='Visit Sagrada Familia',
            description='Visit the famous church',
            planned_date=datetime.now(timezone.utc) + timedelta(days=1),
            diary=diary
        )
        db.session.add(activity)
        db.session.commit()

        assert activity.title == 'Visit Sagrada Familia'
        assert activity.description == 'Visit the famous church'
        assert isinstance(activity.planned_date, datetime)
        assert activity.diary == diary
        assert isinstance(activity.created_at, datetime)
        assert isinstance(activity.updated_at, datetime)
        assert not activity.is_completed
        assert activity.completed_at is None

def test_activity_completion(init_database, app):
    """Test marking an activity as completed."""
    with app.app_context():
        diary = TravelDiary(
            title='Trip to Barcelona',
            location='Barcelona, Spain'
        )
        db.session.add(diary)
        
        activity = Activity(
            title='Visit Sagrada Familia',
            diary=diary
        )
        db.session.add(activity)
        db.session.commit()

        activity.mark_completed('Great experience!')
        db.session.commit()

        assert activity.is_completed
        assert isinstance(activity.completed_at, datetime)
        assert activity.completion_notes == 'Great experience!'

def test_activity_required_fields():
    """Test required fields validation."""
    with pytest.raises(ValueError):
        Activity()  # Missing title and diary

    diary = TravelDiary(
        title='Test Trip',
        location='Test Location'
    )

    with pytest.raises(ValueError):
        Activity(diary=diary)  # Missing title

    with pytest.raises(ValueError):
        Activity(title='Test Activity')  # Missing diary

def test_activity_date_validation(init_database, app):
    """Test planned date validation against diary dates."""
    with app.app_context():
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=7)
        
        diary = TravelDiary(
            title='Trip to Barcelona',
            location='Barcelona, Spain',
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(diary)
        db.session.commit()

        # Test activity planned before trip starts
        with pytest.raises(ValueError):
            activity = Activity(
                title='Early Activity',
                diary=diary,
                planned_date=start_date - timedelta(days=1)
            )
            db.session.add(activity)
            db.session.commit()

        # Test activity planned after trip ends
        with pytest.raises(ValueError):
            activity = Activity(
                title='Late Activity',
                diary=diary,
                planned_date=end_date + timedelta(days=1)
            )
            db.session.add(activity)
            db.session.commit()

def test_activity_to_dict(init_database, app):
    """Test activity to dictionary conversion."""
    with app.app_context():
        diary = TravelDiary(
            title='Trip to Barcelona',
            location='Barcelona, Spain'
        )
        db.session.add(diary)
        
        planned_date = datetime.now(timezone.utc)
        activity = Activity(
            title='Visit Sagrada Familia',
            description='Visit the church',
            planned_date=planned_date,
            diary=diary
        )
        db.session.add(activity)
        db.session.commit()

        activity_dict = activity.to_dict()
        assert activity_dict['title'] == 'Visit Sagrada Familia'
        assert activity_dict['description'] == 'Visit the church'
        dict_date = datetime.fromisoformat(activity_dict['planned_date'])
        # Compare only year, month, day, minute, second
        assert dict_date.year == planned_date.year
        assert dict_date.month == planned_date.month
        assert dict_date.day == planned_date.day
        assert dict_date.minute == planned_date.minute
        assert dict_date.second == planned_date.second
        assert not activity_dict['is_completed']
        assert activity_dict['completed_at'] is None
        assert activity_dict['diary_id'] == diary.id

def test_activity_representation():
    """Test string representation of activity."""
    diary = TravelDiary(
        title='Trip to Barcelona',
        location='Barcelona, Spain'
    )
    activity = Activity(
        title='Visit Sagrada Familia',
        diary=diary
    )
    assert str(activity) == '<Activity: Visit Sagrada Familia>'

def test_activity_default_values(init_database, app):
    """Test default values for activity fields."""
    with app.app_context():
        diary = TravelDiary(
            title='Trip to Barcelona',
            location='Barcelona, Spain'
        )
        db.session.add(diary)
        
        activity = Activity(
            title='Test Activity',
            diary=diary
        )
        db.session.add(activity)
        db.session.commit()

        assert activity.description == ''
        assert activity.planned_date is None
        assert not activity.is_completed
        assert activity.completed_at is None
        assert activity.completion_notes is None

def test_activity_update(init_database, app):
    """Test updating activity details."""
    with app.app_context():
        diary = TravelDiary(
            title='Trip to Barcelona',
            location='Barcelona, Spain'
        )
        db.session.add(diary)
        
        activity = Activity(
            title='Visit Sagrada Familia',
            diary=diary
        )
        db.session.add(activity)
        db.session.commit()

        # Update activity
        activity.title = 'Visit Sagrada Familia Basilica'
        activity.description = 'Updated description'
        activity.planned_date = datetime.now(timezone.utc)
        db.session.commit()

        # Refresh from database
        db.session.refresh(activity)
        assert activity.title == 'Visit Sagrada Familia Basilica'
        assert activity.description == 'Updated description'
        assert isinstance(activity.planned_date, datetime)

def test_activity_diary_relationship(init_database, app):
    """Test activity-diary bidirectional relationship."""
    with app.app_context():
        diary = TravelDiary(
            title='Trip to Barcelona',
            location='Barcelona, Spain'
        )
        db.session.add(diary)
        db.session.commit()

        # Add activities through diary relationship
        activity1 = Activity(title='Morning Activity', diary=diary)
        activity2 = Activity(title='Afternoon Activity', diary=diary)
        db.session.add_all([activity1, activity2])
        db.session.commit()

        # Check relationships
        assert len(diary.activities) == 2
        assert all(activity.diary == diary for activity in diary.activities)
        assert diary.activities[0].title in ['Morning Activity', 'Afternoon Activity']
        assert diary.activities[1].title in ['Morning Activity', 'Afternoon Activity'] 