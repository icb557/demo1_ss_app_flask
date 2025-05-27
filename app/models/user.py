"""User model."""
from datetime import datetime, timezone
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

def get_utc_now():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    """User model."""
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime(timezone=True), default=get_utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)
    active = db.Column(db.Boolean, default=True, nullable=False)

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
        self.active = True

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
        if not self.password_hash:
            return False
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
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'active': self.active
        }

    # Flask-Login interface methods
    def get_id(self):
        """Return the user ID as a unicode string."""
        return str(self.id)

    @property
    def is_active(self):
        """Return whether user is active."""
        return self.active

    @property
    def is_authenticated(self):
        """Return True if user is authenticated."""
        return True

    @property
    def is_anonymous(self):
        """Return False as anonymous users are not supported."""
        return False 