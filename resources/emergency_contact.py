from flask_restful import Resource, reqparse
from models import db, EmergencyContact

class EmergencyContactResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='Name is required')
    parser.add_argument('relationship', type=str, required=True, help='Relationship is required')
    parser.add_argument('phone_number', type=str, required=True, help='Phone number is required')
    parser.add_argument('email', type=str, required=False)
    parser.add_argument('address', type=str, required=False)
    parser.add_argument('user_id', type=int, required=True, help='User ID is required')
    
    def get(self, id=None):
        try:
            if id is None:
                contacts = EmergencyContact.query.all()
                return {"Success": True, "data": [c.to_dict() for c in contacts]}, 200
            else:
                contact = EmergencyContact.query.get(id)
                if not contact:
                    return {"Success": False, "message": "Emergency contact not found"}, 404
                return {"Success": True, "data": contact.to_dict()}, 200
        except Exception as e:
            return {"Success": False, "message": f"Error fetching emergency contact: {str(e)}"}, 500

    def post(self):
        try:
            data = EmergencyContactResource.parser.parse_args()
            contact = EmergencyContact(
                name=data['name'],
                relationship=data['relationship'],
                phone_number=data['phone_number'],
                email=data.get('email'),
                address=data.get('address'),
                user_id=data['user_id']
            )
            db.session.add(contact)
            db.session.commit()
            return {"Success": True, "data": contact.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {"Success": False, "message": f"Error creating emergency contact: {str(e)}"}, 500

    def patch(self, id):
        try:
            contact = EmergencyContact.query.get(id)
            if not contact:
                return {"Success": False, "message": "Emergency contact not found"}, 404
            
            data = EmergencyContactResource.parser.parse_args()
            for field in ['name', 'relationship', 'phone_number', 'email', 'address']:
                if field in data and data[field] is not None:
                    setattr(contact, field, data[field])
            
            db.session.commit()
            return {"Success": True, "data": contact.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            return {"Success": False, "message": f"Error updating emergency contact: {str(e)}"}, 500

    def delete(self, id):
        try:
            contact = EmergencyContact.query.get(id)
            if not contact:
                return {"Success": False, "message": "Emergency contact not found"}, 404
            
            db.session.delete(contact)
            db.session.commit()
            return {"Success": True, "message": "Emergency contact deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"Success": False, "message": f"Error deleting emergency contact: {str(e)}"}, 500