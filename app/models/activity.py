"""Activity model."""
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

class Activity(db.Model):
    """Activity model class."""
    
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    planned_date = db.Column(db.DateTime(timezone=True))
    location = db.Column(db.String(200))
    cost = db.Column(db.Float)
    notes = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False)
    completion_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), default=get_utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)
    completed_at = db.Column(db.DateTime(timezone=True))

    # Relationships
    diary_id = db.Column(db.Integer, db.ForeignKey('travel_diaries.id'), nullable=False)
    diary = db.relationship('TravelDiary', back_populates='activities')

    def __init__(self, title=None, description='', planned_date=None, location=None, cost=None, notes=None, diary=None):
        """Initialize activity with basic data."""
        if not title:
            raise ValueError('Title is required')
        if not diary:
            raise ValueError('Diary is required')
            
        self.title = title
        self.description = description
        self.location = location
        self.cost = cost
        self.notes = notes
        self.diary = diary

        # Validate and set planned_date
        if planned_date:
            # Ensure planned_date is timezone aware
            planned_date = make_timezone_aware(planned_date)
            
            if diary.start_date and diary.end_date:
                # Ensure diary dates are timezone aware
                start_date = make_timezone_aware(diary.start_date)
                end_date = make_timezone_aware(diary.end_date)
                
                if not (start_date <= planned_date <= end_date):
                    raise ValueError('Planned date must be within diary dates')
            self.planned_date = planned_date

        # Set timestamps
        self.created_at = get_utc_now()
        self.updated_at = self.created_at

    def __repr__(self):
        """Return string representation of activity."""
        return f'<Activity: {self.title}>'

    def mark_completed(self, completion_notes=None):
        """Mark the activity as completed."""
        self.is_completed = True
        self.completed_at = get_utc_now()
        if completion_notes:
            self.completion_notes = completion_notes

    def to_dict(self):
        """Convert activity to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'planned_date': self.planned_date.astimezone(timezone.utc).isoformat() if self.planned_date else None,
            'location': self.location,
            'cost': self.cost,
            'notes': self.notes,
            'is_completed': self.is_completed,
            'completion_notes': self.completion_notes,
            'created_at': self.created_at.astimezone(timezone.utc).isoformat() if self.created_at else None,
            'updated_at': self.updated_at.astimezone(timezone.utc).isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.astimezone(timezone.utc).isoformat() if self.completed_at else None,
            'diary_id': self.diary_id
        } 