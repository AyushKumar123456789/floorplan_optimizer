# app/__init__.py

from flask import Flask
from .routes import main
import os
import matplotlib

def create_app():
    app = Flask(__name__)
    
    # Configure Matplotlib to use the 'Agg' backend for non-GUI environments
    matplotlib.use('Agg')
    
    # Register blueprints
    app.register_blueprint(main)
    
    # Ensure the static/images directory exists
    images_dir = os.path.join(app.root_path, 'static', 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    return app
