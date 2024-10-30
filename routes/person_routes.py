from flask import Blueprint, jsonify, request
from models import db, Person, Relationship
from datetime import datetime
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


person_routes = Blueprint('person_routes', __name__)

def get_available_id():
    """Return the lowest available ID in the persons table."""
    existing_ids = {person.id for person in Person.query.all()}
    next_id = 1

    while next_id in existing_ids:
        next_id += 1

    return next_id

@person_routes.route('/persons', methods=['GET'])
def get_persons():
    """Fetch all persons from the database."""
    try:
        persons = Person.query.all()  # Fetch all persons from the database
        return jsonify([{
            "id": person.id,
            "first_name": person.first_name,
            "last_name": person.last_name,
            "gender": person.gender,
            "dob": person.dob.strftime('%Y-%m-%d')
        } for person in persons]), 200
    except Exception as e:
        logger.error(f"Error fetching persons: {e}")
        return jsonify({"error": "Failed to fetch persons"}), 500

@person_routes.route('/persons', methods=['POST'])
def add_person():
    """Add a new person to the database."""
    data = request.json

    required_fields = {'first_name', 'last_name', 'gender', 'dob'}
    if not required_fields.issubset(data):
        missing = required_fields - data.keys()
        logger.warning(f"Missing fields in request data: {missing}")
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

   
    try:
        dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
    except ValueError:
        logger.warning("Invalid date format for dob")
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    
    available_id = get_available_id()

    
    new_person = Person(
        id=available_id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        gender=data['gender'],
        dob=dob
    )

    try:
        # Add the new person to the session
        db.session.add(new_person)
        db.session.commit()
        logger.info(f"Added new person: {new_person.first_name} {new_person.last_name}")
        return jsonify({"id": new_person.id, "message": "Person added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding person: {e}")
        return jsonify({"error": f"Failed to add person: {str(e)}"}), 500

@person_routes.route('/persons/<int:id>', methods=['GET'])
def get_person(id):
    """Fetch a single person by ID."""
    person = Person.query.get(id)
    if not person:
        logger.warning(f"Person with ID {id} not found.")
        return jsonify({"error": "Person not found"}), 404
    
    return jsonify({
        "id": person.id,
        "first_name": person.first_name,
        "last_name": person.last_name,
        "gender": person.gender,
        "dob": person.dob.strftime('%Y-%m-%d')
    }), 200

@person_routes.route('/persons/<int:id>', methods=['PUT'])
def update_person(id):
    """Update an existing person in the database."""
    data = request.json

    person = Person.query.get(id)
    if not person:
        logger.warning(f"Person with ID {id} not found.")
        return jsonify({"error": "Person not found"}), 404

    # Update fields if they are provided
    if 'first_name' in data:
        person.first_name = data['first_name']
    if 'last_name' in data:
        person.last_name = data['last_name']
    if 'gender' in data:
        person.gender = data['gender']
    if 'dob' in data:
        try:
            person.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        except ValueError:
            logger.warning("Invalid date format for dob")
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    try:
        db.session.commit()
        logger.info(f"Updated person ID {id} successfully.")
        return jsonify({"message": "Person updated successfully"}), 200
    except Exception as e:
        db.session.rollback()  
        logger.error(f"Error updating person ID {id}: {e}")
        return jsonify({"error": "Failed to update person"}), 500

@person_routes.route('/persons/<int:id>', methods=['DELETE'])
def delete_person(id):
    """Delete a person from the database."""
    logger.info(f"Attempting to delete person ID {id}.")
    person = Person.query.get(id)
    
    if not person:
        logger.warning(f"Person with ID {id} not found.")
        return jsonify({"error": "Person not found"}), 404

    try:
        
        Relationship.query.filter((Relationship.parent_id == id) | (Relationship.child_id == id)).delete()

        
        db.session.delete(person)
        db.session.commit()
        logger.info(f"Deleted person ID {id} successfully.")
        return jsonify({"message": "Person deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting person ID {id}: {e}")
        return jsonify({"error": "Failed to delete person"}), 500
