"""Integration tests for TravelService."""
import pytest
from datetime import datetime, timezone, timedelta
from app.services.travel_service import TravelService, make_timezone_aware
from app.services.user_service import UserService
from app.models import TravelDiary, Activity
from app import db

def test_create_travel_diary(init_database, app):
    """Test travel diary creation with TravelService."""
    with app.app_context():
        # Create a test user first
        user_service = UserService()
        user = user_service.create_user(
            username='travel_test_user',
            email='travel_test@example.com',
            password='test_password'
        )
        
        service = TravelService()
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=7)
        
        # Test successful creation
        diary = service.create_travel_diary(
            user=user,
            title='Test Travel',
            location='Test Location',
            description='Test description',
            start_date=start_date,
            end_date=end_date
        )
        
        assert diary.title == 'Test Travel'
        assert diary.location == 'Test Location'
        assert diary.description == 'Test description'
        assert diary.user == user
        assert make_timezone_aware(diary.start_date) == start_date
        assert make_timezone_aware(diary.end_date) == end_date
        
        # Test invalid dates
        with pytest.raises(ValueError, match="End date cannot be before start date"):
            service.create_travel_diary(
                user=user,
                title='Invalid Dates Travel',
                location='Test Location',
                start_date=end_date,
                end_date=start_date
            )

def test_get_diary_methods(init_database, app):
    """Test methods to retrieve travel diaries."""
    with app.app_context():
        # Create a test user
        user_service = UserService()
        user = user_service.create_user(
            username='get_travel_user',
            email='get_travel@example.com',
            password='test_password'
        )
        
        service = TravelService()
        start_date = datetime.now(timezone.utc)
        
        # Create test diaries
        diary1 = service.create_travel_diary(
            user=user,
            title='First Travel',
            location='Location 1',
            start_date=start_date,
            end_date=start_date + timedelta(days=7)
        )
        
        diary2 = service.create_travel_diary(
            user=user,
            title='Second Travel',
            location='Location 2',
            start_date=start_date + timedelta(days=10),
            end_date=start_date + timedelta(days=17)
        )
        
        # Test get by ID
        retrieved_diary = service.get_diary_by_id(diary1.id)
        assert retrieved_diary.id == diary1.id
        assert retrieved_diary.title == 'First Travel'
        
        # Test get user diaries
        all_diaries = service.get_user_diaries(user)
        assert len(all_diaries) == 2
        assert all_diaries[0].title == 'First Travel'  # Should be ordered by start_date
        assert all_diaries[1].title == 'Second Travel'
        
        # Test not found case
        with pytest.raises(ValueError, match="Travel diary not found"):
            service.get_diary_by_id(9999)

def test_add_and_manage_activities(init_database, app):
    """Test adding and managing activities in a travel diary."""
    with app.app_context():
        # Create a test user
        user_service = UserService()
        user = user_service.create_user(
            username='activity_test_user',
            email='activity_test@example.com',
            password='test_password'
        )
        
        service = TravelService()
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=7)
        
        # Create a test diary
        diary = service.create_travel_diary(
            user=user,
            title='Activity Test Travel',
            location='Test Location',
            start_date=start_date,
            end_date=end_date
        )
        
        # Test adding activities
        activity1 = service.add_activity(
            diary=diary,
            title='Test Activity 1',
            planned_date=start_date + timedelta(days=1),
            description='Activity description',
            location='Activity location',
            cost=100.0,
            notes='Activity notes'
        )
        
        activity2 = service.add_activity(
            diary=diary,
            title='Test Activity 2',
            planned_date=start_date + timedelta(days=2)
        )
        
        # Test getting diary activities
        activities = service.get_diary_activities(diary)
        assert len(activities) == 2
        assert activities[0].title == 'Test Activity 1'  # Should be ordered by planned_date
        assert activities[1].title == 'Test Activity 2'
        
        # Test activity outside diary dates
        with pytest.raises(ValueError, match="Activity date must be within diary date range"):
            service.add_activity(
                diary=diary,
                title='Invalid Date Activity',
                planned_date=start_date - timedelta(days=1)
            )
        
        # Test marking activity as completed
        completed_activity = service.mark_activity_completed(
            activity1,
            completion_notes='Completed successfully'
        )
        assert completed_activity.is_completed
        assert completed_activity.completion_notes == 'Completed successfully'
        assert completed_activity.completed_at is not None

def test_update_diary(init_database, app):
    """Test updating travel diary information."""
    with app.app_context():
        # Create a test user
        user_service = UserService()
        user = user_service.create_user(
            username='update_travel_user',
            email='update_travel@example.com',
            password='test_password'
        )
        
        service = TravelService()
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=7)
        
        # Create a test diary
        diary = service.create_travel_diary(
            user=user,
            title='Travel to Update',
            location='Original Location',
            start_date=start_date,
            end_date=end_date
        )
        
        # Test updating various fields
        new_start_date = start_date + timedelta(days=1)
        new_end_date = end_date + timedelta(days=1)
        updated_diary = service.update_diary(diary, {
            'title': 'Updated Travel',
            'location': 'Updated Location',
            'description': 'Updated description',
            'start_date': new_start_date,
            'end_date': new_end_date
        })
        
        assert updated_diary.title == 'Updated Travel'
        assert updated_diary.location == 'Updated Location'
        assert updated_diary.description == 'Updated description'
        assert make_timezone_aware(updated_diary.start_date) == new_start_date
        assert make_timezone_aware(updated_diary.end_date) == new_end_date
        
        # Test invalid dates
        with pytest.raises(ValueError, match="End date cannot be before start date"):
            service.update_diary(diary, {
                'start_date': end_date,
                'end_date': start_date
            })

def test_delete_diary(init_database, app):
    """Test travel diary deletion."""
    with app.app_context():
        # Create a test user
        user_service = UserService()
        user = user_service.create_user(
            username='delete_travel_user',
            email='delete_travel@example.com',
            password='test_password'
        )
        
        service = TravelService()
        start_date = datetime.now(timezone.utc)
        
        # Create a test diary with activities
        diary = service.create_travel_diary(
            user=user,
            title='Travel to Delete',
            location='Test Location',
            start_date=start_date,
            end_date=start_date + timedelta(days=7)
        )
        
        # Add some activities
        service.add_activity(
            diary=diary,
            title='Activity 1',
            planned_date=start_date + timedelta(days=1)
        )
        service.add_activity(
            diary=diary,
            title='Activity 2',
            planned_date=start_date + timedelta(days=2)
        )
        
        # Delete the diary
        service.delete_diary(diary)
        
        # Verify diary and activities are deleted
        with pytest.raises(ValueError, match="Travel diary not found"):
            service.get_diary_by_id(diary.id)
        
        # Activities should be deleted due to cascade
        assert Activity.query.filter_by(diary_id=diary.id).count() == 0 