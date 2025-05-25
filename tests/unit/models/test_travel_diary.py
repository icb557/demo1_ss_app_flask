"""Test cases for TravelDiary model."""
import pytest
from datetime import datetime, timezone, timedelta
from app.models import TravelDiary, Activity
from app import db

def test_new_travel_diary(test_user, init_database, app):
    """Test creating a new travel diary entry."""
    with app.app_context():
        diary = TravelDiary(
            title='Trip to Barcelona',
            location='Barcelona, Spain',
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=7),
            description='Amazing trip to Barcelona',
            user=test_user
        )
        db.session.add(diary)
        db.session.commit()

        assert diary.title == 'Trip to Barcelona'
        assert diary.location == 'Barcelona, Spain'
        assert isinstance(diary.start_date, datetime)
        assert isinstance(diary.end_date, datetime)
        assert diary.description == 'Amazing trip to Barcelona'
        assert diary.user == test_user
        assert isinstance(diary.created_at, datetime)
        assert isinstance(diary.updated_at, datetime)

def test_add_activity_to_diary(init_database, app):
    """Test adding an activity to a travel diary."""
    with app.app_context():
        diary = TravelDiary(
            title='Trip to Barcelona',
            location='Barcelona, Spain',
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.session.add(diary)
        
        activity = Activity(
            title='Visit Sagrada Familia',
            description='Visit the famous church',
            planned_date=datetime.now(timezone.utc) + timedelta(days=1),
            diary=diary
        )
        db.session.add(activity)
        db.session.commit()

        assert activity in diary.activities
        assert activity.title == 'Visit Sagrada Familia'
        assert activity.diary == diary
        assert len(diary.activities) == 1

def test_diary_date_validation(init_database, app):
    """Test date validation in travel diary."""
    with app.app_context():
        end_date = datetime.now(timezone.utc)
        start_date = end_date + timedelta(days=1)  # Start date after end date

        with pytest.raises(ValueError):
            diary = TravelDiary(
                title='Invalid Trip',
                location='Test Location',
                start_date=start_date,
                end_date=end_date
            )
            db.session.add(diary)
            db.session.commit()

def test_diary_required_fields():
    """Test required fields validation."""
    with pytest.raises(ValueError):
        TravelDiary()  # Missing title and location

    with pytest.raises(ValueError):
        TravelDiary(title='Test Trip')  # Missing location

    with pytest.raises(ValueError):
        TravelDiary(location='Test Location')  # Missing title

def test_diary_to_dict(init_database, app):
    """Test travel diary to dictionary conversion."""
    with app.app_context():
        diary = TravelDiary(
            title='Trip to Barcelona',
            location='Barcelona, Spain',
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=7),
            description='Amazing trip'
        )
        db.session.add(diary)
        
        activity = Activity(
            title='Visit Sagrada Familia',
            description='Visit the church',
            planned_date=datetime.now(timezone.utc) + timedelta(days=1),
            diary=diary
        )
        db.session.add(activity)
        db.session.commit()

        diary_dict = diary.to_dict()
        assert diary_dict['title'] == 'Trip to Barcelona'
        assert diary_dict['location'] == 'Barcelona, Spain'
        assert diary_dict['description'] == 'Amazing trip'
        assert len(diary_dict['activities']) == 1
        assert diary_dict['activities'][0]['title'] == 'Visit Sagrada Familia'

def test_diary_user_relationship(test_user, init_database, app):
    """Test diary-user relationship."""
    with app.app_context():
        diary = TravelDiary(
            title='My Trip',
            location='Test Location',
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=7),
            user=test_user
        )
        db.session.add(diary)
        db.session.commit()

        assert diary in test_user.travel_diaries
        assert diary.user.username == test_user.username

def test_diary_representation():
    """Test string representation of travel diary."""
    diary = TravelDiary(
        title='Trip to Barcelona',
        location='Barcelona, Spain'
    )
    assert str(diary) == '<TravelDiary: Trip to Barcelona>'

def test_diary_default_values():
    """Test default values for travel diary fields."""
    diary = TravelDiary(
        title='Test Trip',
        location='Test Location'
    )
    assert diary.description == ''
    assert diary.start_date is None
    assert diary.end_date is None
    assert diary.activities == []

def test_cascade_delete(init_database, app):
    """Test that deleting a diary also deletes its activities."""
    with app.app_context():
        diary = TravelDiary(
            title='Trip to Barcelona',
            location='Barcelona, Spain',
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.session.add(diary)
        
        activity1 = Activity(
            title='Visit Sagrada Familia',
            diary=diary
        )
        activity2 = Activity(
            title='Park Güell Tour',
            diary=diary
        )
        db.session.add(activity1)
        db.session.add(activity2)
        db.session.commit()

        # Store activity IDs
        activity_ids = [activity1.id, activity2.id]
        
        # Delete diary
        db.session.delete(diary)
        db.session.commit()

        # Check that activities were deleted
        activities = Activity.query.filter(Activity.id.in_(activity_ids)).all()
        assert len(activities) == 0 