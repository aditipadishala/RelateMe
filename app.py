from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from routes.person_routes import person_routes
from routes.relation_routes import relation_routes
from models import db, Person, Relationship  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/databasename'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)


app.register_blueprint(person_routes)
app.register_blueprint(relation_routes)


with app.app_context():
    db.create_all()

@app.route('/')
def home():
   
    persons = Person.query.all()
    persons_list = [
        {
            'id': p.id,
            'first_name': p.first_name,
            'last_name': p.last_name,
            'gender': p.gender,
            'dob': p.dob.strftime('%Y-%m-%d')
        } for p in persons
    ]
    
 
    relationships = Relationship.query.all()
    relationships_list = [
        {
            'id': r.id,
            'parent_id': r.parent_id,
            'child_id': r.child_id
        } for r in relationships
    ]

    return jsonify({
        'persons': persons_list,
        'relationships': relationships_list
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
