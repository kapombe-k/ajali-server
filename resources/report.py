from flask_restful import Resource, reqparse
from models import db, Report, MediaAttachment
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt
import uuid
import os
from datetime import datetime


class ReportResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "incident", type=str, required=True, help="incident type is required"
    )
    parser.add_argument("details", type=str, help="Please provide a detailed message")
    parser.add_argument("latitude", type=str, help="Select a location")
    parser.add_argument("longitude", type=str, help="Select a location")

    def allowed_file(self, filename):
        ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "avi", "mov", "webm"}
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def validate_file(self, file):
        # Check file size (limit to 5MB)
        if len(file.read()) > 5 * 1024 * 1024:
            return False, "File size exceeds 5MB limit"
        file.seek(0)  # Reset file pointer
        
        # Check file type
        if not self.allowed_file(file.filename):
            return False, "File type not allowed"
            
        return True, "File is valid"
    
    def save_media(self, report_id, file):
        # Validate file
        is_valid, message = self.validate_file(file)
        if not is_valid:
            return None, message
            
        if file and self.allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"

            #create a media directory
            media_dir = os.path.join(current_app.config['UPLOAD_FOLDER'],str(report_id))
            os.makedirs(media_dir,exist_ok=True)

            # save the file
            filepath =os.path.join(media_dir, filename)
            file.save(filepath)

            #create media record in the db
            media = MediaAttachment(
                report_id=report_id,
                media_type=file.content_type,
                file_url=filepath,
                uploaded_at=datetime.now()
            )
            db.session.add(media)
            return media, "File saved successfully"
        return None, "File not saved"


   # @jwt_required()
    def post(self):
        data = request.get_json()
        args = self.parser.parse_args()
        
        # Validate required fields
        if not data or "user_id" not in data:
            return {"message": "user_id is required"}, 400
            
        if not args["incident"]:
            return {"message": "incident is required"}, 400

        try:
            report = Report(
                user_id=data["user_id"],
                incident=args["incident"],
                details=args.get("details"),
                latitude=float(data["latitude"]) if data.get("latitude") else 0.0,
                longitude=float(data["longitude"]) if data.get("longitude") else 0.0,
            )
            db.session.add(report)
            db.session.commit()

            # file uploads will be handled here
            if 'media' in request.files:
                files = request.files.getlist('media')
                for file in files:
                    if file.filename =='':
                        continue
                    media, message = self.save_media(report.id, file)
                    if media is None:
                        db.session.rollback()
                        return {"message": "Failed to save media", "error": message}, 400
                    db.session.commit()

            return report.to_dict(), 201
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating report: {str(e)}")
            return {"message": "Failed to create report", "error": "An error occurred while creating the report"}, 400
        
    @jwt_required()
    def get(self, report_id=None):
        try:
            claims = get_jwt()
            role = claims.get("role")
            if role != "admin":
                return {"Success": False, "message": "Admin access required"}, 403

            if report_id:
                report = Report.query.get(report_id)
                if report:
                    return {"Success": True, "data": report.to_dict()}, 200
                return {"Success": False, "message": "Report not found"}, 404

            reports = Report.query.all()
            return {"Success": True, "data": [r.to_dict() for r in reports]}, 200
        except Exception as e:
            return {"Success": False, "message": f"An error occurred while fetching reports: {str(e)}"}, 500

    @jwt_required()
    def patch(self, report_id):
        try:
            report = Report.query.get(report_id)
            if not report:
                return {"Success": False, "message": "Report not found"}, 404

            data = request.get_json()
            for field in ["user_id", "details", "incident", "latitude", "longitude"]:
                if field in data:
                    setattr(report, field, data[field])

            db.session.commit()
            return {"Success": True, "data": report.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            return {"Success": False, "message": f"An error occurred while updating report: {str(e)}"}, 500

    @jwt_required()
    def delete(self, report_id):
        try:
            report = Report.query.get(report_id)
            if not report:
                return {"Success": False, "message": "Report not found"}, 404

            #we must add delete for associated media files
            for media in report.media_attachments:
                try:
                    if os.path.exists(media.file_url):
                        os.remove(media.file_url)
                except OSError as e:
                    current_app.logger.error(f"Error deleting media file:{str(e)}")
                db.session.delete(media)

            db.session.delete(report)
            db.session.commit()
            return {"Success": True, "message": "Report deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"Success": False, "message": f"An error occurred while deleting report: {str(e)}"}, 500


class MediaResource(Resource):
    def get(self, report_id):
        try:
            report = Report.query.get(report_id)
            if report:
                media = report.media_attachments
                return {"Success": True, "data": [m.to_dict() for m in media]}, 200
            return {"Success": False, "message": "Report not found"}, 404
        except Exception as e:
            return {"Success": False, "message": f"An error occurred while fetching media: {str(e)}"}, 500

    def post(self, report_id):
        try:
            report = Report.query.get(report_id)
            if not report:
                return {"Success": False, "message": "Report not found"}, 404
            
            if 'media' not in request.files:
                return {"Success": False, "message": "No media files provided"}, 400
            
            files = request.files.getlist('media')
            if not files:
                return {"Success": False, "message": "No files have been selected"}, 400
            
            saved_files = []
            for file in files:
                if file.filename == '':
                    continue
                
                # use the above save_media method
                media, message = ReportResource().save_media(report_id, file)
                if media:
                    saved_files.append(media.to_dict())
                else:
                    db.session.rollback()
                    return {"Success": False, "message": "Failed to save media", "error": message}, 400

            db.session.commit()
            return {"Success": True, "data": saved_files}, 201
        
        except Exception as e:
            db.session.rollback()
            return {"Success": False, "message": "Failed to upload media", "error": str(e)}, 500

    def delete(self, report_id):
        try:
            report = Report.query.get(report_id)
            if not report:
                return {"Success": False, "message": "Report not found"}, 404

            for media in report.media_attachments:
                db.session.delete(media)
            db.session.commit()
            return {"Success": True, "message": "Media deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"Success": False, "message": f"An error occurred while deleting media: {str(e)}"}, 500
