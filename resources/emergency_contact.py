
from flask import Blueprint, request, jsonify
from models import db, EmergencyContact

emergency_contact_bp = Blueprint('emergency_contact', __name__)

@emergency_contact_bp.route('/', methods=['GET'])
def get_contacts():
    contacts = EmergencyContact.query.all()
    return jsonify([c.to_dict() for c in contacts]), 200

@emergency_contact_bp.route('/<int:id>', methods=['GET'])
def get_contact(id):
    contact = EmergencyContact.query.get_or_404(id)
    return jsonify(contact.to_dict()), 200

@emergency_contact_bp.route('/', methods=['POST'])
def create_contact():
    data = request.get_json()
    contact = EmergencyContact(
        name=data['name'],
        relationship=data['relationship'],
        phone_number=data['phone_number'],
        email=data.get('email'),
        address=data.get('address')
    )
    db.session.add(contact)
    db.session.commit()
    return jsonify(contact.to_dict()), 201

@emergency_contact_bp.route('/<int:id>', methods=['PATCH'])
def update_contact(id):
    contact = EmergencyContact.query.get_or_404(id)
    data = request.get_json()
    for field in ['name', 'relationship', 'phone_number', 'email', 'address']:
        if field in data:
            setattr(contact, field, data[field])
    db.session.commit()
    return jsonify(contact.to_dict()), 200

@emergency_contact_bp.route('/<int:id>', methods=['DELETE'])
def delete_contact(id):
    contact = EmergencyContact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    return {'message': 'Deleted successfully'}, 204