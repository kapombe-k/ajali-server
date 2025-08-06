from flask_restful import Resource, reqparse
from models import db, Location
from sqlalchemy.exc import SQLAlchemyError

class LocationResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('latitude', type=float, required=True, help='Latitude is required')
    parser.add_argument('longitude', type=float, required=True, help='Longitude is required')
    parser.add_argument('address', type=str, help='Address is optional')
    parser.add_argument('report_id', type=int, required=True, help='Report ID is required')

    def get(self, location_id=None):
        if location_id:
            location = Location.query.get(location_id)
            if location:
                return location.to_dict()
            return {"message": "Location not found"}, 404

        locations = Location.query.all()
        return [loc.to_dict() for loc in locations]

    def post(self):
        data = LocationResource.parser.parse_args()

        try:
            location = Location(**data)
            db.session.add(location)
            db.session.commit()
            return location.to_dict(), 201
        except Exception as e:
            return {'message': str(e)}, 400
        except SQLAlchemyError:
            db.session.rollback()
            return {'message': 'Database error'}, 500

    def patch(self, location_id):
        location = Location.query.get(location_id)
        if not location:
            return {"message": "Location not found"}, 404

        data = LocationResource.parser.parse_args()
        for key, value in data.items():
            setattr(location, key, value)

        try:
            db.session.commit()
            return location.to_dict()
        except Exception as e:
            return {"message": str(e)}, 400
        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "Database error"}, 500

    def delete(self, location_id):
        location = Location.query.get(location_id)
        if not location:
            return {"message": "Location not found"}, 404

        try:
            db.session.delete(location)
            db.session.commit()
            return {"message": "Location deleted"}
        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "Database error"}, 500
