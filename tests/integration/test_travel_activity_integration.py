"""Integration tests for TravelDiary and Activity models."""
import pytest
from datetime import datetime, timezone, timedelta
from app.models import User, TravelDiary, Activity
from app import db

def test_travel_diary_activity_relationship(init_database, app):
    """Test the relationship between TravelDiary and Activity models."""
    with app.app_context():
        # Create a test user
        user = User(
            username='travel_test_user',
            email='travel@test.com'
        )
        db.session.add(user)
        db.session.commit()

        # Create a travel diary
        travel_diary = TravelDiary(
            title='Test Travel Diary',
            location='Test Location',
            description='A test travel diary',
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=7),
            user=user
        )
        db.session.add(travel_diary)
        db.session.commit()

        # Create activities for the travel diary
        activity1 = Activity(
            title='Test Activity 1',
            description='Description for test activity 1',
            planned_date=datetime.now(timezone.utc) + timedelta(days=1),
            location='Test Location 1',
            diary=travel_diary
        )
        activity2 = Activity(
            title='Test Activity 2',
            description='Description for test activity 2',
            planned_date=datetime.now(timezone.utc) + timedelta(days=2),
            location='Test Location 2',
            diary=travel_diary
        )

        db.session.add_all([activity1, activity2])
        db.session.commit()

        # Test relationships
        assert len(travel_diary.activities) == 2
        assert travel_diary.activities[0].title == 'Test Activity 1'
        assert travel_diary.activities[1].title == 'Test Activity 2'
        assert activity1.diary == travel_diary
        assert activity2.diary == travel_diary

def test_activity_crud_operations(init_database, app):
    """Test CRUD operations for Activity model."""
    with app.app_context():
        # Create a test user and travel diary
        user = User(
            username='activity_crud_user',
            email='activity_crud@test.com'
        )
        db.session.add(user)
        db.session.commit()

        travel_diary = TravelDiary(
            title='CRUD Test Diary',
            location='CRUD Test Location',
            description='Testing CRUD operations',
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=7),
            user=user
        )
        db.session.add(travel_diary)
        db.session.commit()

        # Create an activity
        activity = Activity(
            title='CRUD Test Activity',
            description='Testing CRUD operations',
            planned_date=datetime.now(timezone.utc) + timedelta(days=1),
            location='Test Location',
            diary=travel_diary
        )
        db.session.add(activity)
        db.session.commit()

        # Read
        retrieved_activity = Activity.query.filter_by(title='CRUD Test Activity').first()
        assert retrieved_activity is not None
        assert retrieved_activity.description == 'Testing CRUD operations'

        # Update
        retrieved_activity.location = 'Updated Location'
        db.session.commit()
        updated_activity = db.session.get(Activity, retrieved_activity.id)
        assert updated_activity.location == 'Updated Location'

        # Delete
        db.session.delete(retrieved_activity)
        db.session.commit()
        deleted_activity = db.session.get(Activity, retrieved_activity.id)
        assert deleted_activity is None

def test_cascade_delete_travel_diary(init_database, app):
    """Test cascade delete between TravelDiary and Activity."""
    with app.app_context():
        # Create test user and travel diary
        user = User(
            username='cascade_travel_user',
            email='cascade_travel@test.com'
        )
        db.session.add(user)
        db.session.commit()

        travel_diary = TravelDiary(
            title='Cascade Test Diary',
            location='Cascade Test Location',
            description='Testing cascade operations',
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=7),
            user=user
        )
        db.session.add(travel_diary)
        db.session.commit()

        # Create multiple activities
        activities = [
            Activity(
                title=f'Cascade Activity {i}',
                description=f'Description for cascade activity {i}',
                planned_date=datetime.now(timezone.utc) + timedelta(days=i),
                location=f'Location {i}',
                diary=travel_diary
            )
            for i in range(3)
        ]
        db.session.add_all(activities)
        db.session.commit()

        # Verify activities were created
        assert Activity.query.filter_by(diary_id=travel_diary.id).count() == 3

        # Delete travel diary and verify cascade
        db.session.delete(travel_diary)
        db.session.commit()

        # Verify all related activities were deleted
        assert Activity.query.filter_by(diary_id=travel_diary.id).count() == 0 