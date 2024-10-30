import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'username://postgres:password@localhost:5432/database_name')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
