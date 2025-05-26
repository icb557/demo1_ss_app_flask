"""Views for the main blueprint."""
from flask import jsonify
from app.routes import main_bp

@main_bp.route('/')
def index():
    """Index route."""
    return jsonify({'message': 'Welcome to the Flask API'}) 