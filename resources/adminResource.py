# adminResource.py

from flask_restful import Resource, reqparse
from flask import current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models import User
from models import Report
from datetime import datetime, timezone
#from utils import send_email_notification
# from utils import send_sms_notification  # Uncomment if implemented


def is_admin(user_id):
    user = User.query.get(user_id)
    return user and user.role == "admin"


class AdminResource(Resource):
    @jwt_required()
    def get(self, report_id=None):
        current_user = get_jwt_identity()

        if not is_admin(current_user):
            return {"message": "Admin access required"}, 403

        if report_id:
            report = Report.query.get(report_id)
            if not report:
                return {"message": "report not found"}, 404
            return self.serialize_report(report), 200

        page = request.args.get("page", default=1, type=int)
        per_page = min(request.args.get("per_page", default=10, type=int), 100)

        reports = Report.query.paginate(
            page=page, per_page=per_page, error_out=False
        ).items
        return {"reports": [self.serialize_report(r) for r in reports]}, 200

    @jwt_required()
    def patch(self, report_id):
        current_user = get_jwt_identity()

        if not is_admin(current_user):
            return {"message": "Admin access required"}, 403

        report = Report.query.get(report_id)
        if not report:
            return {"message": "report not found"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument("status", required=True, help="Status is required")
        args = parser.parse_args()

        valid_statuses = ["pending", "under investigation", "rejected", "resolved"]
        if args["status"] not in valid_statuses:
            return {"message": "Invalid status"}, 400

        old_status = report.status
        new_status = args["status"]

        try:
            report.status = new_status
            report.updated_at = datetime.now(timezone.utc)
            db.session.commit()

            self.notify_user(report, old_status, new_status)

            current_app.logger.info(
                f"Admin {current_user} updated report #{report.id} from {old_status} to {new_status}"
            )

            return {
                "message": f"Status updated from {old_status} to {new_status}",
                "report": {
                    "id": report.id,
                    "title": report.title,
                    "status": report.status,
                    "user_id": report.user_id,
                },
            }, 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Admin {current_user} failed to update report #{report.id}: {str(e)}"
            )
            return {"message": f"Error updating status: {str(e)}"}, 500

    @jwt_required()
    def delete(self, report_id):
        current_user = get_jwt_identity()

        if not is_admin(current_user):
            return {"message": "Admin access required"}, 403

        report = Report.query.get(report_id)
        if not report:
            return {"message": "report not found"}, 404

        try:
            db.session.delete(report)
            db.session.commit()
            current_app.logger.info(f"Admin {current_user} deleted report #{report.id}")

            return {"message": f"report #{report_id} deleted successfully"}, 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Admin {current_user} failed to delete report #{report.id}: {str(e)}"
            )
            return {"message": f"Error deleting report: {str(e)}"}, 500

    def serialize_report(self, report):
        return {
            "id": report.id,
            "type": report.type,
            "title": report.title,
            "description": report.description,
            "latitude": report.latitude,
            "longitude": report.longitude,
            "images": report.images or [],
            "status": report.status,
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "updated_at": report.updated_at.isoformat() if report.updated_at else None,
            "user_id": report.user_id,
        }

    # def notify_user(self, report, old_status, new_status):
    #     if old_status == new_status:
    #         return

    #     user = User.query.get(report.user_id)
    #     if not user or not user.email:
    #         return

    #     subject = f"Update on Your Emergency Report #{report.id}"
    #     body = f"""
    #     Hi {user.username},

    #     Your report titled "{report.title}" has a status change.

    #     Old Status: {old_status}
    #     New Status: {new_status}

    #     Please check your dashboard for more details.
    #     """

        # try:
        #     send_email_notification(user.email, subject, body)

            
        # except Exception as e:
        #     current_app.logger.error(f"Failed to notify user #{user.id}: {str(e)}")
