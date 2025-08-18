
from flask_restful import Resource
from flask import request
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt
from models import db, Report, StatusUpdate
#from sqlalchemy.exc import SQLAlchemyError

class ReportStatusUpdateResource(Resource):
    @jwt_required(optional=True)
    def get(self, report_id):
        try:
            claims = get_jwt()
            role = claims.get("role")
            if role != "admin":
                return {"Success": False, "message": "Admin access required"}, 403

            report = Report.query.get(report_id)
            if not report:
                return {"Success": False, "message": "Report not found"}, 404

            latest_status_update = (StatusUpdate.query.filter_by(report_id=report_id).order_by(StatusUpdate.timestamp.desc()).first())

            response = {
                "Success": True,
                "data": {
                    "id": report.id,
                    "incident": report.incident,
                    "details": report.details,
                    "latitude": report.latitude,
                    "longitude": report.longitude,
                    # "current_status": report.status,
                    "latest_status_update": {
                        "status": latest_status_update.status if latest_status_update else None,
                        "updated_by": latest_status_update.updated_by if latest_status_update else None,
                        "timestamp": latest_status_update.timestamp.isoformat() if latest_status_update else None,
                    } if latest_status_update else None,
                }
            }
            return response, 200
        except Exception as e:
            return {"Success": False, "message": "An error occurred while fetching report status"}, 500

    @jwt_required()
    def post(self, report_id):
        try:
            claims = get_jwt()
            role = claims.get("role")
            updated_by = claims.get("sub")

            if role != "admin":
                return {"Success": False, "message": "Admin access required"}, 403

            data = request.get_json()
            new_status = data.get('status')
            valid_statuses = ['under investigation', 'rejected', 'resolved']
            if new_status not in valid_statuses:
                return {"Success": False, "message": f"Invalid status. Must be one of {valid_statuses}"}, 400

            report = Report.query.get(report_id)
            if not report:
                return {"Success": False, "message": "Report not found"}, 404

            status_update = StatusUpdate(
                report_id=report_id,
                updated_by=updated_by,
                status=new_status,
                timestamp=datetime.now()
            )
            report.status = new_status

            db.session.add(status_update)
            db.session.commit()

            return {"Success": True, "message": f"Report status updated to '{new_status}'"}, 200

        except Exception as e:
            db.session.rollback()
            return {"Success": False, "message": "An error occurred while updating report status"}, 500