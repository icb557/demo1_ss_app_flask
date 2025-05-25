"""Initialize database migrations."""
from flask_migrate import init, migrate, upgrade
from app import create_app, db

def init_migrations():
    """Initialize and run initial migration."""
    app = create_app()
    
    with app.app_context():
        # Initialize migrations
        init()
        
        # Create initial migration
        migrate()
        
        # Apply migration
        upgrade()

if __name__ == '__main__':
    init_migrations() 