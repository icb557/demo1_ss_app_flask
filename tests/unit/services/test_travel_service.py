"""Unit tests for TravelService."""
import pytest
from datetime import datetime, timezone
from app.models import User, TravelDiary, Activity
from app.services.travel_service import TravelService
from app import db

class TestTravelService:
    """Test cases for TravelService."""

    def test_create_travel_diary(self):
        """Test creating a travel diary."""
        user = User(username='test_user', email='test@example.com')
        diary_data = {
            'title': 'Trip to Barcelona',
            'location': 'Barcelona, Spain',
            'start_date': datetime.now(timezone.utc),
            'end_date': datetime.now(timezone.utc),
            'description': 'Amazing trip to Barcelona'
        }
        
        travel_service = TravelService()
        diary = travel_service.create_travel_diary(user, **diary_data)
        
        assert diary.title == diary_data['title']
        assert diary.user == user

    def test_add_activity(self):
        """Test adding an activity to a travel diary."""
        travel_service = TravelService()
        diary = TravelDiary(title='Trip to Barcelona', location='Barcelona, Spain')
        
        activity_data = {
            'title': 'Visit Sagrada Familia',
            'description': 'Visit the famous church',
            'planned_date': datetime.now(timezone.utc)
        }
        
        activity = travel_service.add_activity(diary, **activity_data)
        assert activity.title == activity_data['title']
        assert activity.diary == diary

    def test_get_diary_activities(self):
        """Test getting all activities for a travel diary."""
        travel_service = TravelService()
        diary = TravelDiary(title='Trip to Barcelona', location='Barcelona, Spain')
        
        activity1 = Activity(title='Activity 1', diary=diary)
        activity2 = Activity(title='Activity 2', diary=diary)
        db.session.add_all([activity1, activity2])
        db.session.commit()

        activities = travel_service.get_diary_activities(diary)
        assert len(activities) == 2
        assert all(activity.diary == diary for activity in activities) 