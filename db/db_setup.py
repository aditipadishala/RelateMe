# db/db_setup.py
from flask_sqlalchemy import SQLAlchemy
from config import Config  # Import the Config class

db = SQLAlchemy()

def init_db(app):
    app.config.from_object(Config)  # Load the configuration from the Config class
    db.init_app(app)  # Initialize the SQLAlchemy instance with the app
