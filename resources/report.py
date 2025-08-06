from flask_restful import Resource, reqparse
from models import db, Report, MediaAttachment
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError
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
        ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def save_media(self, report_id, file):
        if file and self.allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"

            #create a media directory
            media_dir = os.path.join(current_app.config['UPLOAD_FOLDER'],str(report_id))
            os.makedirs(media_dir,exist_ok=True)

            # save rthe file
            filepath =os.path.join(media_dir, filename)
            file.save(filepath)

            #create media record in the db
            media = MediaAttachment(
                report_id=report_id,
                media_type=file.content_type,
                file_url=filepath,
                uploaded_at=datetime()
            )
            db.session.add(media)
            return media
        return None


   # @jwt_required()
    def post(self):
        data = request.get_json()
        args = self.parser.parse_args()

        try:
            report = Report(
                user_id=data["user_id"],
                incident=args["incident"],
                details=args.get("details"),
                latitude=data["latitude"],
                longitude=data["longitude"],
            )
            db.session.add(report)
            db.session.commit()

            # file uploads will be handled here
            if 'media' in request.files:
                files = request.files.getlist('media')
                for file in files:
                    if file.filename =='':
                        continue
                    self.save_media(file, report.id)
                    db.session.commit()

            return report.to_dict(), 201
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating report: {str(e)}")
            return {"message": "Failed to create report", "error": str(e)}, 400
        
    @jwt_required()
    def get(self, id=None):
        claims = get_jwt()
        role = claims.get("role")
        if role != "admin":
            return {"message": "Admin access required"}, 403

        if id:
            report = Report.query.get(id)
            if report:
                return report.to_dict(), 200
            return {"message": "Report not found"}, 404

        reports = Report.query.all()
        return [r.to_dict() for r in reports], 200

    @jwt_required()
    def patch(self, id=None):
        report = Report.query.get(id)
        if not report:
            return {"message": "Report not found"}, 404

        data = request.get_json()
        for field in ["user_id", "details", "incident", "latitude", "longitude"]:
            if field in data:
                setattr(report, field, data[field])

        try:
            db.session.commit()
            return report.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {"message": str(e)}, 400

    @jwt_required()
    def delete(self, id=None):
        report = Report.query.get(id)
        if not report:
            return {"message": "Report not found"}, 404

        try:
            #we must add delete for associated media files
            for media in report.media_attachment:
                try:
                    if os.path.exists(media.filepath):
                        os.remove(media.filepath)
                except OSError as e:
                    current_app.logger.error(f"Error deleting media file:{str(e)}")
                db.session.delete(media)

            db.session.delete(report)
            db.session.commit()
            return {"message": "Report deleted successfully"}, 200
        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "Database error"}, 500


class MediaResource(Resource):
    def get(self, id=None):
        report = Report.query.get(id)
        if report:
            media = report.media_attachment
            return [m.to_dict() for m in media], 200
        return {"message": "Media not found"}, 404
    

    def post(self, id=None):
        report = Report.query.get(id)
        if not report:
            return {'message':'Report not found'}, 404
        
        try:
            if 'media' not in request.files:
                return {'message':'No media files provided'}, 403
            
            files =request.files.getlist('media')
            if not files:
                return {'message':'No files have been selected'}, 401
            
            saved_files=[]
            for file in files:
                if file.filename=='':
                    continue
                
                # use the above save_media method
                media = ReportResource().save_media(file, report.id)
                if media:
                    saved_files.append(media.to_dict())

            db.session.commit()
            return saved_files, 201
        
        except Exception as e:
            db.session.rollback()
            return {"message":"Faied to upload media", "error": str(e)}, 400

    def delete(self, id=None):
        report = Report.query.get(id)
        if not report:
            return {"message": "Report not found"}, 404

        try:
            for media in report.media_attachment:
                db.session.delete(media)
            db.session.commit()
            return {"message": "Media deleted successfully"}, 200
        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "Database error: Media not deleted"}, 500
