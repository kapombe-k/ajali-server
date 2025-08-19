from flask_restful import Resource, reqparse
from models import db, Location

class LocationResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('latitude', type=float, required=True, help='Latitude is required')
    parser.add_argument('longitude', type=float, required=True, help='Longitude is required')
    parser.add_argument('address', type=str, help='Address is optional')
    parser.add_argument('report_id', type=int, required=True, help='Report ID is required')

    def get(self, location_id=None):
        try:
            if location_id:
                location = Location.query.get(location_id)
                if location:
                    return {"Success": True, "data": location.to_dict()}, 200
                return {"Success": False, "message": "Location not found"}, 404

            locations = Location.query.all()
            return {"Success": True, "data": [loc.to_dict() for loc in locations]}, 200
        except Exception as e:
            return {"Success": False, "message": f"An error occurred while fetching locations: {str(e)}"}, 500

    def post(self):
        try:
            data = LocationResource.parser.parse_args()
            location = Location(**data)
            db.session.add(location)
            db.session.commit()
            return {"Success": True, "data": location.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {"Success": False, "message": f"An error occurred while creating location: {str(e)}"}, 500

    def patch(self, location_id):
        try:
            location = Location.query.get(location_id)
            if not location:
                return {"Success": False, "message": "Location not found"}, 404

            data = LocationResource.parser.parse_args()
            for key, value in data.items():
                setattr(location, key, value)

            db.session.commit()
            return {"Success": True, "data": location.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            return {"Success": False, "message": f"An error occurred while updating location: {str(e)}"}, 500

    def delete(self, location_id):
        try:
            location = Location.query.get(location_id)
            if not location:
                return {"Success": False, "message": "Location not found"}, 404

            db.session.delete(location)
            db.session.commit()
            return {"Success": True, "message": "Location deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"Success": False, "message": f"An error occurred while deleting location: {str(e)}"}, 500
