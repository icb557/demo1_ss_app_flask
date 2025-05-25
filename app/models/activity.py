"""Activity model."""
from datetime import datetime, timezone
from app import db

def get_utc_now():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)

class Activity(db.Model):
    """Activity model class."""
    
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    planned_date = db.Column(db.DateTime(timezone=True))
    is_completed = db.Column(db.Boolean, default=False)
    completion_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), default=get_utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)
    completed_at = db.Column(db.DateTime(timezone=True))

    # Relationships
    diary_id = db.Column(db.Integer, db.ForeignKey('travel_diaries.id'), nullable=False)

    def __init__(self, title=None, description='', planned_date=None, diary=None):
        """Initialize activity with basic data."""
        if not title:
            raise ValueError('Title is required')
        if not diary:
            raise ValueError('Diary is required')
            
        self.title = title
        self.description = description
        self.diary = diary

        # Validate and set planned_date
        if planned_date:
            # Ensure planned_date is timezone aware
            if planned_date.tzinfo is None:
                planned_date = planned_date.replace(tzinfo=timezone.utc)
            
            if diary.start_date and diary.end_date:
                # Ensure diary dates are timezone aware
                start_date = diary.start_date if diary.start_date.tzinfo else diary.start_date.replace(tzinfo=timezone.utc)
                end_date = diary.end_date if diary.end_date.tzinfo else diary.end_date.replace(tzinfo=timezone.utc)
                
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
        def format_date(date):
            """Format date with timezone info."""
            if not date:
                return None
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            return date.isoformat()

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'planned_date': format_date(self.planned_date),
            'is_completed': self.is_completed,
            'completion_notes': self.completion_notes,
            'created_at': format_date(self.created_at),
            'updated_at': format_date(self.updated_at),
            'completed_at': format_date(self.completed_at),
            'diary_id': self.diary_id
        } 