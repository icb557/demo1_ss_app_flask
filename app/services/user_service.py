"""User service module."""
import re
from datetime import datetime, timezone
from app.models import User
from app import db

class UserService:
    """Service class for handling user operations."""

    def __init__(self):
        """Initialize UserService."""
        self.email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    def create_user(self, username: str, email: str, password: str) -> User:
        """
        Create a new user.
        
        Args:
            username: The username for the new user
            email: The email address for the new user
            password: The password for the new user
            
        Returns:
            User: The newly created user object
            
        Raises:
            ValueError: If username/email already exists or email format is invalid
        """
        # Validate email format
        if not self.email_regex.match(email):
            raise ValueError("Invalid email format")

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            raise ValueError("Username already exists")

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            raise ValueError("Email already exists")

        user = User(username=username, email=email)
        user.password = password  # This will hash the password
        
        db.session.add(user)
        db.session.commit()
        
        return user

    def get_user_by_id(self, user_id: int) -> User:
        """
        Get a user by their ID.
        
        Args:
            user_id: The ID of the user to retrieve
            
        Returns:
            User: The user object if found
            
        Raises:
            ValueError: If user is not found
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    def get_user_by_username(self, username: str) -> User:
        """
        Get a user by their username.
        
        Args:
            username: The username to search for
            
        Returns:
            User: The user object if found
            
        Raises:
            ValueError: If user is not found
        """
        user = User.query.filter_by(username=username).first()
        if not user:
            raise ValueError("User not found")
        return user

    def get_user_by_email(self, email: str) -> User:
        """
        Get a user by their email address.
        
        Args:
            email: The email address to search for
            
        Returns:
            User: The user object if found
            
        Raises:
            ValueError: If user is not found
        """
        user = User.query.filter_by(email=email).first()
        if not user:
            raise ValueError("User not found")
        return user

    def update_user(self, user: User, update_data: dict) -> User:
        """
        Update a user's information.
        
        Args:
            user: The user object to update
            update_data: Dictionary containing the fields to update
            
        Returns:
            User: The updated user object
            
        Raises:
            ValueError: If trying to update to an email that already exists
        """
        if 'email' in update_data:
            # Check if new email already exists for a different user
            existing_user = User.query.filter_by(email=update_data['email']).first()
            if existing_user and existing_user.id != user.id:
                raise ValueError("Email already exists")
            user.email = update_data['email']

        if 'password' in update_data:
            user.password = update_data['password']

        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return user

    def delete_user(self, user: User) -> None:
        """
        Delete a user.
        
        Args:
            user: The user object to delete
        """
        db.session.delete(user)
        db.session.commit() 