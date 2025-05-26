"""Travel service module."""
from datetime import datetime, timezone
from typing import List, Optional
from app.models import TravelDiary, Activity, User
from app import db

def make_timezone_aware(dt: datetime) -> datetime:
    """Make a datetime timezone aware if it isn't already."""
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

class TravelService:
    """Service class for handling travel diary operations."""

    def create_travel_diary(self, user: User, title: str, location: str,
                          start_date: datetime, end_date: Optional[datetime] = None,
                          description: Optional[str] = None) -> TravelDiary:
        """
        Create a new travel diary.
        
        Args:
            user: The user who owns the diary
            title: The title of the diary
            location: The location of the trip
            start_date: The start date of the trip
            end_date: Optional end date of the trip
            description: Optional description of the trip
            
        Returns:
            TravelDiary: The newly created travel diary object
            
        Raises:
            ValueError: If end_date is before start_date
        """
        # Ensure dates are timezone aware
        start_date = make_timezone_aware(start_date)
        if end_date:
            end_date = make_timezone_aware(end_date)
            if end_date < start_date:
                raise ValueError("End date cannot be before start date")

        diary = TravelDiary(
            title=title,
            location=location,
            description=description,
            start_date=start_date,
            end_date=end_date,
            user=user
        )
        
        db.session.add(diary)
        db.session.commit()
        
        return diary

    def get_diary_by_id(self, diary_id: int) -> TravelDiary:
        """
        Get a travel diary by ID.
        
        Args:
            diary_id: The ID of the diary to retrieve
            
        Returns:
            TravelDiary: The travel diary object
            
        Raises:
            ValueError: If diary is not found
        """
        diary = TravelDiary.query.get(diary_id)
        if not diary:
            raise ValueError("Travel diary not found")
        return diary

    def get_user_diaries(self, user: User) -> List[TravelDiary]:
        """
        Get all travel diaries for a user.
        
        Args:
            user: The user whose diaries to retrieve
            
        Returns:
            List[TravelDiary]: List of travel diaries
        """
        return TravelDiary.query.filter_by(user=user).order_by(TravelDiary.start_date).all()

    def add_activity(self, diary: TravelDiary, title: str, planned_date: datetime,
                    description: Optional[str] = None, location: Optional[str] = None,
                    cost: Optional[float] = None, notes: Optional[str] = None) -> Activity:
        """
        Add an activity to a travel diary.
        
        Args:
            diary: The diary to add the activity to
            title: The title of the activity
            planned_date: The planned date for the activity
            description: Optional description of the activity
            location: Optional specific location for the activity
            cost: Optional cost of the activity
            notes: Optional additional notes
            
        Returns:
            Activity: The newly created activity object
            
        Raises:
            ValueError: If planned_date is outside diary date range
        """
        # Ensure planned_date is timezone aware
        planned_date = make_timezone_aware(planned_date)

        # Ensure diary dates are timezone aware
        start_date = make_timezone_aware(diary.start_date)
        end_date = make_timezone_aware(diary.end_date) if diary.end_date else None
        
        if end_date and planned_date > end_date:
            raise ValueError("Activity date must be within diary date range")
        if planned_date < start_date:
            raise ValueError("Activity date must be within diary date range")

        activity = Activity(
            title=title,
            description=description,
            planned_date=planned_date,
            location=location,
            cost=cost,
            notes=notes,
            diary=diary
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return activity

    def get_diary_activities(self, diary: TravelDiary) -> List[Activity]:
        """
        Get all activities for a travel diary.
        
        Args:
            diary: The diary whose activities to retrieve
            
        Returns:
            List[Activity]: List of activities
        """
        return Activity.query.filter_by(diary=diary).order_by(Activity.planned_date).all()

    def mark_activity_completed(self, activity: Activity, completion_notes: Optional[str] = None) -> Activity:
        """
        Mark an activity as completed.
        
        Args:
            activity: The activity to mark as completed
            completion_notes: Optional notes about completion
            
        Returns:
            Activity: The updated activity object
        """
        activity.mark_completed(completion_notes)
        db.session.commit()
        return activity

    def update_diary(self, diary: TravelDiary, update_data: dict) -> TravelDiary:
        """
        Update a travel diary's information.
        
        Args:
            diary: The diary object to update
            update_data: Dictionary containing the fields to update
            
        Returns:
            TravelDiary: The updated diary object
            
        Raises:
            ValueError: If trying to update with invalid dates
        """
        if 'title' in update_data:
            diary.title = update_data['title']
        if 'location' in update_data:
            diary.location = update_data['location']
        if 'description' in update_data:
            diary.description = update_data['description']

        if 'start_date' in update_data:
            diary.start_date = make_timezone_aware(update_data['start_date'])
        if 'end_date' in update_data:
            diary.end_date = make_timezone_aware(update_data['end_date'])

        if diary.start_date and diary.end_date and diary.end_date < diary.start_date:
            raise ValueError("End date cannot be before start date")

        db.session.commit()
        return diary

    def delete_diary(self, diary: TravelDiary) -> None:
        """
        Delete a travel diary and all its activities.
        
        Args:
            diary: The diary to delete
        """
        db.session.delete(diary)
        db.session.commit() 