"""Task model."""
from datetime import datetime, timezone
from app import db

# Constantes para validación
VALID_CATEGORIES = {'personal', 'work', 'shopping', 'health', 'general', 'study'}
VALID_PRIORITIES = {'low', 'medium', 'high'}
VALID_STATUSES = {'pending', 'completed', 'cancelled'}

def get_utc_now():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)

def make_timezone_aware(dt):
    """Make a datetime timezone aware if it isn't already."""
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

class Task(db.Model):
    """Task model class."""
    
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    due_date = db.Column(db.DateTime(timezone=True))
    category = db.Column(db.String(20), default='general')
    priority = db.Column(db.String(10), default='medium')
    status = db.Column(db.String(20), default='pending')
    completion_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), default=get_utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)
    completed_at = db.Column(db.DateTime(timezone=True))

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='tasks')

    def __init__(self, title=None, description='', due_date=None, category='general', 
                 priority='medium', status='pending', user=None):
        """Initialize task with basic data."""
        if not title:
            raise ValueError('Title is required')
            
        self.title = title
        self.description = description
        self.due_date = make_timezone_aware(due_date) if due_date else None
        self.user = user
        
        # Validate and set category
        if category not in VALID_CATEGORIES:
            raise ValueError(f'Invalid category. Must be one of: {", ".join(VALID_CATEGORIES)}')
        self.category = category
        
        # Validate and set priority
        if priority not in VALID_PRIORITIES:
            raise ValueError(f'Invalid priority. Must be one of: {", ".join(VALID_PRIORITIES)}')
        self.priority = priority
        
        # Validate and set status
        if status not in VALID_STATUSES:
            raise ValueError(f'Invalid status. Must be one of: {", ".join(VALID_STATUSES)}')
        self.status = status

        # Set timestamps
        self.created_at = get_utc_now()
        self.updated_at = self.created_at

    def __repr__(self):
        """Return string representation of task."""
        return f'<Task: {self.title}>'

    def mark_completed(self, completion_notes=None):
        """Mark the task as completed."""
        self.status = 'completed'
        self.completed_at = get_utc_now()
        if completion_notes:
            self.completion_notes = completion_notes

    def is_overdue(self):
        """Check if the task is overdue."""
        if self.due_date and self.status != 'completed':
            return get_utc_now() > make_timezone_aware(self.due_date)
        return False

    def to_dict(self):
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'completion_notes': self.completion_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'user_id': self.user_id
        } 