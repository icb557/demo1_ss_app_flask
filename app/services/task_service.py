"""Task service module."""
from datetime import datetime, timezone
from typing import List, Optional
from app.models import Task, User
from app import db

class TaskService:
    """Service class for handling task operations."""

    VALID_CATEGORIES = ['personal', 'work', 'shopping', 'health', 'study']
    VALID_STATUSES = ['pending', 'in_progress', 'completed', 'cancelled']

    def create_task(self, user: User, title: str, category: str, status: str = 'pending',
                   description: Optional[str] = None, due_date: Optional[datetime] = None) -> Task:
        """
        Create a new task.
        
        Args:
            user: The user who owns the task
            title: The title of the task
            category: The category of the task
            status: The initial status of the task (defaults to 'pending')
            description: Optional description of the task
            due_date: Optional due date for the task
            
        Returns:
            Task: The newly created task object
            
        Raises:
            ValueError: If category or status is invalid
        """
        # Validate category
        if category not in self.VALID_CATEGORIES:
            raise ValueError("Invalid category")

        # Validate status
        if status not in self.VALID_STATUSES:
            raise ValueError("Invalid status")

        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            category=category,
            status=status,
            user=user
        )
        
        db.session.add(task)
        db.session.commit()
        
        return task

    def get_task_by_id(self, task_id: int) -> Task:
        """
        Get a task by its ID.
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            Task: The task object if found
            
        Raises:
            ValueError: If task is not found
        """
        task = Task.query.get(task_id)
        if not task:
            raise ValueError("Task not found")
        return task

    def get_user_tasks(
        self,
        user: User,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Task]:
        """Get tasks for a user with optional filters."""
        query = Task.query.filter_by(user=user)
        
        if status:
            if status not in self.VALID_STATUSES:
                raise ValueError(f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}")
            query = query.filter_by(status=status)
            
        if category:
            if category not in self.VALID_CATEGORIES:
                raise ValueError(f"Invalid category. Must be one of: {', '.join(self.VALID_CATEGORIES)}")
            query = query.filter_by(category=category)
        
        query = query.order_by(Task.due_date.asc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()

    def update_task(self, task: Task, update_data: dict) -> Task:
        """
        Update a task's information.
        
        Args:
            task: The task object to update
            update_data: Dictionary containing the fields to update
            
        Returns:
            Task: The updated task object
            
        Raises:
            ValueError: If trying to update with invalid category or status
        """
        if 'category' in update_data:
            if update_data['category'] not in self.VALID_CATEGORIES:
                raise ValueError("Invalid category")
            task.category = update_data['category']

        if 'status' in update_data:
            if update_data['status'] not in self.VALID_STATUSES:
                raise ValueError("Invalid status")
            task.status = update_data['status']
            if update_data['status'] == 'completed':
                task.completed_at = datetime.now(timezone.utc)

        if 'title' in update_data:
            task.title = update_data['title']

        if 'description' in update_data:
            task.description = update_data['description']

        if 'due_date' in update_data:
            task.due_date = update_data['due_date']

        task.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return task

    def mark_task_completed(self, task: Task) -> Task:
        """
        Mark a task as completed.
        
        Args:
            task: The task object to mark as completed
            
        Returns:
            Task: The updated task object
        """
        return self.update_task(task, {'status': 'completed'})

    def delete_task(self, task: Task) -> None:
        """
        Delete a task.
        
        Args:
            task: The task object to delete
        """
        db.session.delete(task)
        db.session.commit() 