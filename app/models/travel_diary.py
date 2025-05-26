"""Travel Diary model."""
from datetime import datetime, timezone
from app import db

def get_utc_now():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)

def make_timezone_aware(dt):
    """Make a datetime timezone aware if it isn't already."""
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

class TravelDiary(db.Model):
    """Travel Diary model class."""
    
    __tablename__ = 'travel_diaries'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    start_date = db.Column(db.DateTime(timezone=True))
    end_date = db.Column(db.DateTime(timezone=True))
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), default=get_utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='travel_diaries')
    activities = db.relationship('Activity', back_populates='diary', cascade='all, delete-orphan')

    def __init__(self, title=None, location=None, description='', start_date=None, end_date=None, user=None):
        """Initialize travel diary with basic data."""
        if not title:
            raise ValueError('Title is required')
        if not location:
            raise ValueError('Location is required')
            
        self.title = title
        self.location = location
        self.description = description
        self.user = user

        # Validate and set dates
        if start_date:
            # Ensure start_date is timezone aware
            start_date = make_timezone_aware(start_date)
            self.start_date = start_date
            
        if end_date:
            # Ensure end_date is timezone aware
            end_date = make_timezone_aware(end_date)
            self.end_date = end_date

        if start_date and end_date and end_date < start_date:
            raise ValueError('End date cannot be before start date')

        # Set timestamps
        self.created_at = get_utc_now()
        self.updated_at = self.created_at

    def __repr__(self):
        """Return string representation of travel diary."""
        return f'<TravelDiary: {self.title}>'

    def add_activity(self, activity):
        """Add an activity to the travel diary."""
        if activity not in self.activities:
            self.activities.append(activity)

    def to_dict(self):
        """Convert travel diary to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'location': self.location,
            'description': self.description,
            'start_date': self.start_date.astimezone(timezone.utc).isoformat() if self.start_date else None,
            'end_date': self.end_date.astimezone(timezone.utc).isoformat() if self.end_date else None,
            'created_at': self.created_at.astimezone(timezone.utc).isoformat() if self.created_at else None,
            'updated_at': self.updated_at.astimezone(timezone.utc).isoformat() if self.updated_at else None,
            'user_id': self.user_id,
            'activities': [activity.to_dict() for activity in self.activities]
        } 