"""User model."""
from datetime import datetime, timezone
import re
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

def get_utc_now():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)

class User(db.Model):
    """User model."""
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime(timezone=True), default=get_utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    tasks = db.relationship('Task', back_populates='user', cascade='all, delete-orphan')
    travel_diaries = db.relationship('TravelDiary', back_populates='user', cascade='all, delete-orphan')

    def __init__(self, username, email, password=None):
        """Initialize user with basic data."""
        self.username = username
        self.email = self._validate_email(email)
        if password:
            self.password = password
        
        # Set timestamps
        self.created_at = get_utc_now()
        self.updated_at = self.created_at

    def __repr__(self):
        """Return string representation of user."""
        return f'<User {self.username}>'

    @property
    def password(self):
        """Prevent password from being accessed."""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Set password to a hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches."""
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def _validate_email(email):
        """Validate email format."""
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_regex.match(email):
            raise ValueError('Invalid email format')
        return email

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 