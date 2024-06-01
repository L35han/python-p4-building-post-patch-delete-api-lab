from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Bakery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

class BakedGood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    bakery_id = db.Column(db.Integer, db.ForeignKey('bakery.id'), nullable=False)
    bakery = db.relationship('Bakery', backref=db.backref('baked_goods', lazy=True))

@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    new_message = Message(body=data['body'], username=data['username'])
    db.session.add(new_message)
    db.session.commit()
    return jsonify({
        'id': new_message.id,
        'body': new_message.body,
        'username': new_message.username,
        'created_at': new_message.created_at,
        'updated_at': new_message.updated_at
    }), 201

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.all()
    return jsonify([{
        'id': message.id,
        'body': message.body,
        'username': message.username,
        'created_at': message.created_at,
        'updated_at': message.updated_at
    } for message in messages])

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    data = request.get_json()
    message = Message.query.get_or_404(id)
    if 'body' in data:
        message.body = data['body']
    db.session.commit()
    return jsonify({
        'id': message.id,
        'body': message.body,
        'username': message.username,
        'created_at': message.created_at,
        'updated_at': message.updated_at
    })

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    return '', 204

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    data = request.get_json()
    name = data.get('name')
    bakery_id = data.get('bakery_id')

    if not name or not bakery_id:
        return jsonify({"error": "Name and bakery_id are required"}), 400

    new_baked_good = BakedGood(name=name, bakery_id=bakery_id)
    db.session.add(new_baked_good)
    db.session.commit()

    return jsonify({
        'id': new_baked_good.id,
        'name': new_baked_good.name,
        'bakery_id': new_baked_good.bakery_id
    }), 201

@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.get_or_404(id)
    data = request.get_json()
    name = data.get('name')

    if name:
        bakery.name = name
        db.session.commit()

    return jsonify({
        'id': bakery.id,
        'name': bakery.name
    })

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get_or_404(id)
    db.session.delete(baked_good)
    db.session.commit()

    return jsonify({"message": f"Baked good {id} successfully deleted."}), 200

@app.route('/bakeries', methods=['GET'])
def get_bakeries():
    bakeries = Bakery.query.all()
    return jsonify([{'id': bakery.id, 'name': bakery.name} for bakery in bakeries])

@app.route('/baked_goods', methods=['GET'])
def get_baked_goods():
    baked_goods = BakedGood.query.all()
    return jsonify([{
        'id': baked_good.id,
        'name': baked_good.name,
        'bakery_id': baked_good.bakery_id
    } for baked_good in baked_goods])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5555, debug=True)
