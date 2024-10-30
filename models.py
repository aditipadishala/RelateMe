from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    dob = db.Column(db.Date, nullable=False)

class Relationship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
