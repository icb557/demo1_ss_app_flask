"""Unit tests for TravelService."""
import pytest
from datetime import datetime, timezone, timedelta
from app.models import User, TravelDiary, Activity
from app.services.travel_service import TravelService
from app import db

@pytest.fixture
def travel_service():
    """Fixture for TravelService."""
    return TravelService()

@pytest.fixture
def sample_diary_data():
    """Fixture for sample travel diary data."""
    start_date = datetime.now(timezone.utc)
    return {
        'title': 'Trip to Barcelona',
        'location': 'Barcelona, Spain',
        'start_date': start_date,
        'end_date': start_date + timedelta(days=7),
        'description': 'Amazing trip to Barcelona'
    }

@pytest.fixture
def sample_activity_data():
    """Fixture for sample activity data."""
    return {
        'title': 'Visit Sagrada Familia',
        'description': 'Visit the famous church',
        'planned_date': datetime.now(timezone.utc) + timedelta(days=1),
        'location': 'Sagrada Familia, Barcelona',
        'cost': 25.0,
        'notes': 'Remember to book tickets in advance'
    }

class TestTravelService:
    """Test cases for TravelService."""

    def test_create_travel_diary_success(self, init_database, travel_service, test_user, sample_diary_data):
        """Test successful travel diary creation."""
        diary = travel_service.create_travel_diary(test_user, **sample_diary_data)
        
        assert diary.title == sample_diary_data['title']
        assert diary.location == sample_diary_data['location']
        assert diary.start_date.replace(tzinfo=None) == sample_diary_data['start_date'].replace(tzinfo=None)
        assert diary.end_date.replace(tzinfo=None) == sample_diary_data['end_date'].replace(tzinfo=None)
        assert diary.description == sample_diary_data['description']
        assert diary.user == test_user
        assert isinstance(diary.created_at, datetime)

    def test_create_travel_diary_invalid_dates(self, init_database, travel_service, test_user):
        """Test travel diary creation with end date before start date."""
        invalid_data = {
            'title': 'Invalid Trip',
            'location': 'Test Location',
            'start_date': datetime.now(timezone.utc) + timedelta(days=7),
            'end_date': datetime.now(timezone.utc),
            'description': 'Test Description'
        }
        
        with pytest.raises(ValueError) as exc_info:
            travel_service.create_travel_diary(test_user, **invalid_data)
        assert str(exc_info.value) == "End date cannot be before start date"

    def test_get_diary_by_id_success(self, init_database, travel_service, test_user, sample_diary_data):
        """Test successfully getting travel diary by ID."""
        diary = travel_service.create_travel_diary(test_user, **sample_diary_data)
        db.session.add(diary)
        db.session.commit()

        retrieved_diary = travel_service.get_diary_by_id(diary.id)
        assert retrieved_diary == diary
        assert retrieved_diary.title == sample_diary_data['title']

    def test_get_diary_by_id_not_found(self, init_database, travel_service):
        """Test getting non-existent travel diary by ID."""
        with pytest.raises(ValueError) as exc_info:
            travel_service.get_diary_by_id(999)
        assert str(exc_info.value) == "Travel diary not found"

    def test_get_user_diaries(self, init_database, travel_service, test_user):
        """Test getting all travel diaries for a user."""
        # Create multiple diaries
        diary1_data = {'title': 'Trip 1', 'location': 'Location 1', 'start_date': datetime.now(timezone.utc)}
        diary2_data = {'title': 'Trip 2', 'location': 'Location 2', 'start_date': datetime.now(timezone.utc)}
        
        diary1 = travel_service.create_travel_diary(test_user, **diary1_data)
        diary2 = travel_service.create_travel_diary(test_user, **diary2_data)
        
        db.session.add_all([diary1, diary2])
        db.session.commit()

        diaries = travel_service.get_user_diaries(test_user)
        assert len(diaries) == 2
        assert all(diary.user == test_user for diary in diaries)

    def test_add_activity_success(self, init_database, travel_service, test_user, sample_diary_data, sample_activity_data):
        """Test successfully adding activity to travel diary."""
        diary = travel_service.create_travel_diary(test_user, **sample_diary_data)
        db.session.add(diary)
        db.session.commit()

        activity = travel_service.add_activity(diary, **sample_activity_data)
        
        assert activity.title == sample_activity_data['title']
        assert activity.description == sample_activity_data['description']
        assert activity.planned_date.replace(tzinfo=None) == sample_activity_data['planned_date'].replace(tzinfo=None)
        assert activity.location == sample_activity_data['location']
        assert activity.cost == sample_activity_data['cost']
        assert activity.notes == sample_activity_data['notes']
        assert activity.diary == diary
        assert not activity.is_completed

    def test_add_activity_invalid_date(self, init_database, travel_service, test_user, sample_diary_data):
        """Test adding activity with date outside diary range."""
        diary = travel_service.create_travel_diary(test_user, **sample_diary_data)
        db.session.add(diary)
        db.session.commit()

        invalid_activity_data = {
            'title': 'Invalid Activity',
            'planned_date': sample_diary_data['end_date'] + timedelta(days=1)
        }
        
        with pytest.raises(ValueError) as exc_info:
            travel_service.add_activity(diary, **invalid_activity_data)
        assert str(exc_info.value) == "Activity date must be within diary date range"

    def test_get_diary_activities(self, init_database, travel_service, test_user, sample_diary_data):
        """Test getting all activities for a travel diary."""
        diary = travel_service.create_travel_diary(test_user, **sample_diary_data)
        
        activity1_data = {'title': 'Activity 1', 'planned_date': sample_diary_data['start_date'] + timedelta(days=1)}
        activity2_data = {'title': 'Activity 2', 'planned_date': sample_diary_data['start_date'] + timedelta(days=2)}
        
        activity1 = travel_service.add_activity(diary, **activity1_data)
        activity2 = travel_service.add_activity(diary, **activity2_data)
        
        db.session.add_all([activity1, activity2])
        db.session.commit()

        activities = travel_service.get_diary_activities(diary)
        assert len(activities) == 2
        assert all(activity.diary == diary for activity in activities)

    def test_mark_activity_completed(self, init_database, travel_service, test_user, sample_diary_data, sample_activity_data):
        """Test marking an activity as completed."""
        diary = travel_service.create_travel_diary(test_user, **sample_diary_data)
        activity = travel_service.add_activity(diary, **sample_activity_data)
        db.session.add_all([diary, activity])
        db.session.commit()
        
        completed_activity = travel_service.mark_activity_completed(activity)
        assert completed_activity.is_completed
        assert isinstance(completed_activity.completed_at, datetime)

    def test_update_diary_success(self, init_database, travel_service, test_user, sample_diary_data):
        """Test successful travel diary update."""
        diary = travel_service.create_travel_diary(test_user, **sample_diary_data)
        db.session.add(diary)
        db.session.commit()
        
        update_data = {
            'title': 'Updated Trip',
            'description': 'Updated Description',
            'location': 'Updated Location'
        }
        updated_diary = travel_service.update_diary(diary, update_data)
        
        assert updated_diary.title == update_data['title']
        assert updated_diary.description == update_data['description']
        assert updated_diary.location == update_data['location']
        assert updated_diary.updated_at > updated_diary.created_at

    def test_update_diary_invalid_dates(self, init_database, travel_service, test_user, sample_diary_data):
        """Test updating diary with invalid dates."""
        diary = travel_service.create_travel_diary(test_user, **sample_diary_data)
        db.session.add(diary)
        db.session.commit()
        
        invalid_update = {
            'start_date': datetime.now(timezone.utc) + timedelta(days=7),
            'end_date': datetime.now(timezone.utc)
        }
        
        with pytest.raises(ValueError) as exc_info:
            travel_service.update_diary(diary, invalid_update)
        assert str(exc_info.value) == "End date cannot be before start date"

    def test_delete_diary(self, init_database, travel_service, test_user, sample_diary_data):
        """Test travel diary deletion."""
        diary = travel_service.create_travel_diary(test_user, **sample_diary_data)
        db.session.add(diary)
        db.session.commit()
        
        travel_service.delete_diary(diary)
        
        with pytest.raises(ValueError):
            travel_service.get_diary_by_id(diary.id) 