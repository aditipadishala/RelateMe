from flask import Blueprint, jsonify, request
from models import db, Person, Relationship  
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

relation_routes = Blueprint('relation_routes', __name__)

@relation_routes.route('/relations', methods=['POST'])
def add_relation():
    """Add a new parent-child relation to the database."""
    data = request.json
    logger.info(f"Received data for adding relation: {data}")

    required_fields = {'parent_id', 'child_id'}
    if not required_fields.issubset(data):
        missing = required_fields - data.keys()
        logger.warning(f"Missing fields in request data: {missing}")
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    parent = Person.query.get(data['parent_id'])
    child = Person.query.get(data['child_id'])

    if not parent:
        logger.warning(f"Parent with ID {data['parent_id']} not found")
        return jsonify({"error": "Parent not found"}), 404
    if not child:
        logger.warning(f"Child with ID {data['child_id']} not found")
        return jsonify({"error": "Child not found"}), 404

    existing_relation = Relationship.query.filter_by(parent_id=data['parent_id'], child_id=data['child_id']).first()
    if existing_relation:
        logger.info(f"Relation already exists between Parent {data['parent_id']} and Child {data['child_id']}")
        return jsonify({"error": "Relation already exists"}), 400

    new_relation = Relationship(parent_id=data['parent_id'], child_id=data['child_id'])

    try:
        db.session.add(new_relation)
        db.session.commit()
        logger.info(f"Relation created successfully: Parent {parent.id}, Child {child.id}")
        return jsonify({"message": "Relation created successfully", "id": new_relation.id}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating relation: {e}")
        return jsonify({"error": "Failed to create relation"}), 500

@relation_routes.route('/relations', methods=['DELETE'])
def delete_relation():
    """Delete an existing relationship between two persons."""
    data = request.json
    logger.info(f"Received data for deleting relation: {data}")

    required_fields = {'parent_id', 'child_id'}
    if not required_fields.issubset(data):
        missing = required_fields - data.keys()
        logger.warning(f"Missing fields in request data: {missing}")
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    relation = Relationship.query.filter_by(parent_id=data['parent_id'], child_id=data['child_id']).first()

    if not relation:
        logger.warning("Relation not found for deletion")
        return jsonify({"error": "Relation not found"}), 404

    try:
        db.session.delete(relation)
        db.session.commit()
        logger.info(f"Relation deleted successfully: Parent {data['parent_id']}, Child {data['child_id']}")
        return jsonify({"message": "Relation deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting relation: {e}")
        return jsonify({"error": "Failed to delete relation"}), 500

@relation_routes.route('/cousins/<int:person_id>', methods=['GET'])
def list_cousins(person_id):
    """Returns a list of all 1st level cousins for a given person along with their parents and grandparents."""
    logger.info(f"Request received to list cousins for person ID: {person_id}")

    person = Person.query.get(person_id)
    if not person:
        logger.warning(f"Person with ID {person_id} not found")
        return jsonify({"error": "Person not found"}), 404

    
    parents = Relationship.query.filter_by(child_id=person_id).all()
    parent_ids = [relation.parent_id for relation in parents]
    parent_names = [{'id': person.id, 'first_name': person.first_name, 'last_name': person.last_name} for person in Person.query.filter(Person.id.in_(parent_ids)).all()]
    logger.info(f"Found parents for person ID {person_id}: {parent_names}")

    
    grandparent_ids = set()
    for parent_id in parent_ids:
        grandparents = Relationship.query.filter_by(child_id=parent_id).all()
        grandparent_ids.update([relation.parent_id for relation in grandparents])
    grandparent_names = [{'id': person.id, 'first_name': person.first_name, 'last_name': person.last_name} for person in Person.query.filter(Person.id.in_(grandparent_ids)).all()]
    logger.info(f"Grandparents for person ID {person_id}: {grandparent_names}")

    
    aunt_uncle_ids = set()
    for grandparent_id in grandparent_ids:
        siblings = Relationship.query.filter_by(parent_id=grandparent_id).all()
        aunt_uncle_ids.update([sibling.child_id for sibling in siblings])
    aunt_uncle_ids.difference_update(parent_ids)  # Exclude the person's parents

    aunt_uncle_names = [{'id': person.id, 'first_name': person.first_name, 'last_name': person.last_name} for person in Person.query.filter(Person.id.in_(aunt_uncle_ids)).all()]
    logger.info(f"Aunts and uncles for person ID {person_id}: {aunt_uncle_names}")

    
    cousin_ids = set()
    for aunt_uncle_id in aunt_uncle_ids:
        cousins = Relationship.query.filter_by(parent_id=aunt_uncle_id).all()
        cousin_ids.update([cousin.child_id for cousin in cousins])
    logger.info(f"Cousins IDs for person ID {person_id}: {cousin_ids}")

    
    cousin_ids.discard(person_id)

    
    cousins = Person.query.filter(Person.id.in_(cousin_ids)).all()
    cousin_list = [{'id': cousin.id, 'first_name': cousin.first_name, 'last_name': cousin.last_name} for cousin in cousins]

    logger.info(f"Listed cousins for person ID {person_id}: {cousin_list}")

    
    response = {
        'parents': parent_names,
        'grandparents': grandparent_names,
        'aunts_and_uncles': aunt_uncle_names,
        'cousins': cousin_list
    }

    return jsonify(response), 200
