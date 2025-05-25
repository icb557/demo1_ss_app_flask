"""Integration tests for travel diary service."""
import pytest
from datetime import datetime, timedelta
from app.services import TravelDiaryService
from app.models import TravelDiary, Activity

def test_create_travel_diary(app, test_user):
    """Test travel diary creation."""
    with app.app_context():
        diary = TravelDiaryService.create_diary(
            user=test_user,
            title='Trip to Barcelona',
            location='Barcelona, Spain',
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=5),
            description='Amazing trip planned'
        )
        assert diary.title == 'Trip to Barcelona'
        assert diary.user == test_user
        
        # Verify diary was saved and get view data
        diary_data = TravelDiaryService.get_diary_with_details(diary.id)
        assert diary_data['diary'].location == 'Barcelona, Spain'
        assert 'activities' in diary_data
        assert 'related_tasks' in diary_data

def test_add_activity_to_diary(app, test_user):
    """Test adding activity to travel diary."""
    with app.app_context():
        diary = TravelDiaryService.create_diary(
            user=test_user,
            title='Trip to Barcelona'
        )
        
        activity = TravelDiaryService.add_activity(
            diary=diary,
            title='Visit Sagrada Familia',
            description='Visit the famous church',
            planned_date=datetime.utcnow() + timedelta(days=1)
        )
        
        assert activity in diary.activities
        assert activity.title == 'Visit Sagrada Familia'
        
        # Verify in database
        saved_diary = TravelDiary.query.get(diary.id)
        assert len(saved_diary.activities) == 1
        assert saved_diary.activities[0].title == 'Visit Sagrada Familia'

def test_get_user_diaries(app, test_user):
    """Test getting user's travel diaries."""
    with app.app_context():
        # Create multiple diaries
        TravelDiaryService.create_diary(test_user, 'Trip to Barcelona')
        TravelDiaryService.create_diary(test_user, 'Trip to Paris')
        
        diaries = TravelDiaryService.get_user_diaries(test_user)
        assert len(diaries) == 2
        assert any(d.title == 'Trip to Barcelona' for d in diaries)
        assert any(d.title == 'Trip to Paris' for d in diaries)

def test_mark_activity_completed(app, test_user):
    """Test marking activity as completed."""
    with app.app_context():
        diary = TravelDiaryService.create_diary(test_user, 'Trip to Barcelona')
        activity = TravelDiaryService.add_activity(
            diary=diary,
            title='Visit Sagrada Familia'
        )
        
        updated_activity = TravelDiaryService.mark_activity_completed(activity)
        assert updated_activity.is_completed
        assert isinstance(updated_activity.completed_at, datetime)
        
        # Verify in database
        saved_activity = Activity.query.get(activity.id)
        assert saved_activity.is_completed

def test_get_upcoming_activities(app, test_user):
    """Test getting upcoming activities."""
    with app.app_context():
        diary = TravelDiaryService.create_diary(test_user, 'Trip to Barcelona')
        
        # Add activities with different dates
        today = datetime.utcnow()
        TravelDiaryService.add_activity(
            diary=diary,
            title='Today Activity',
            planned_date=today
        )
        TravelDiaryService.add_activity(
            diary=diary,
            title='Tomorrow Activity',
            planned_date=today + timedelta(days=1)
        )
        
        upcoming = TravelDiaryService.get_upcoming_activities(diary)
        assert len(upcoming) == 1
        assert upcoming[0].title == 'Tomorrow Activity'

def test_search_diaries(app, test_user):
    """Test searching travel diaries."""
    with app.app_context():
        TravelDiaryService.create_diary(
            user=test_user,
            title='Trip to Barcelona',
            location='Barcelona, Spain'
        )
        TravelDiaryService.create_diary(
            user=test_user,
            title='Trip to Madrid',
            location='Madrid, Spain'
        )
        
        # Search by location
        spain_trips = TravelDiaryService.search_diaries(test_user, location='Spain')
        assert len(spain_trips) == 2
        
        # Search by title
        barcelona_trips = TravelDiaryService.search_diaries(test_user, title='Barcelona')
        assert len(barcelona_trips) == 1
        assert barcelona_trips[0].title == 'Trip to Barcelona'

def test_diary_dashboard_data(app, test_user):
    """Test getting diary data for dashboard view."""
    with app.app_context():
        # Create diaries with different dates
        TravelDiaryService.create_diary(
            user=test_user,
            title='Current Trip',
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=3)
        )
        TravelDiaryService.create_diary(
            user=test_user,
            title='Future Trip',
            start_date=datetime.utcnow() + timedelta(days=10),
            end_date=datetime.utcnow() + timedelta(days=15)
        )
        
        dashboard_data = TravelDiaryService.get_dashboard_data(test_user)
        assert len(dashboard_data['current_trips']) == 1
        assert len(dashboard_data['upcoming_trips']) == 1
        assert 'trip_statistics' in dashboard_data

def test_diary_list_view(app, test_user):
    """Test getting diary list with pagination and filters."""
    with app.app_context():
        # Create test diaries
        TravelDiaryService.create_diary(test_user, 'Spain Trip', location='Spain')
        TravelDiaryService.create_diary(test_user, 'France Trip', location='France')
        
        # Test pagination
        page = TravelDiaryService.get_paginated_diaries(test_user, page=1, per_page=10)
        assert len(page.items) == 2
        assert page.total == 2
        
        # Test location filter
        spain_diaries = TravelDiaryService.get_filtered_diaries(test_user, location='Spain')
        assert len(spain_diaries) == 1
        assert spain_diaries[0].title == 'Spain Trip'

def test_activity_management(app, test_user):
    """Test activity management with view data."""
    with app.app_context():
        diary = TravelDiaryService.create_diary(test_user, 'Paris Trip')
        
        # Add activities
        activity = TravelDiaryService.add_activity(
            diary=diary,
            title='Visit Eiffel Tower',
            description='Evening visit',
            planned_date=datetime.utcnow() + timedelta(days=1)
        )
        
        # Get activity view data
        activity_data = TravelDiaryService.get_activity_details(activity.id)
        assert activity_data['activity'].title == 'Visit Eiffel Tower'
        assert 'related_tasks' in activity_data
        assert 'timeline_position' in activity_data

def test_diary_summary_and_stats(app, test_user):
    """Test getting diary summary and statistics for views."""
    with app.app_context():
        diary = TravelDiaryService.create_diary(test_user, 'Europe Trip')
        
        # Add activities
        act1 = TravelDiaryService.add_activity(diary, 'Activity 1')
        act2 = TravelDiaryService.add_activity(diary, 'Activity 2')
        TravelDiaryService.mark_activity_completed(act1)
        
        # Get summary data
        summary = TravelDiaryService.get_diary_summary(diary.id)
        assert summary['total_activities'] == 2
        assert summary['completed_activities'] == 1
        assert summary['completion_percentage'] == 50
        assert 'activity_timeline' in summary

def test_search_and_filter_view(app, test_user):
    """Test search and filter functionality for views."""
    with app.app_context():
        # Create test data
        spain_diary = TravelDiaryService.create_diary(
            user=test_user,
            title='Spain Adventure',
            location='Barcelona, Spain'
        )
        TravelDiaryService.create_diary(
            user=test_user,
            title='French Journey',
            location='Paris, France'
        )
        
        # Test search results view
        search_results = TravelDiaryService.search_diaries_for_view(
            user=test_user,
            query='Spain',
            include_activities=True
        )
        assert len(search_results['diaries']) == 1
        assert search_results['diaries'][0].id == spain_diary.id
        assert 'matched_activities' in search_results
        assert 'highlight_terms' in search_results 