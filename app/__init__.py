"""Flask application initialization."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """Create Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints only if not testing
    if not app.config.get('TESTING', False):
        from app.routes import main_bp
        app.register_blueprint(main_bp)

    return app 