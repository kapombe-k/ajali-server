import os
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api
from datetime import timedelta
from models import db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from resources.user import UserResources, LoginResource
from resources.status_update import ReportStatusUpdateResource
from resources.report import ReportResource
from resources.location import LocationResource


# import the configs stored inside the env file
load_dotenv()

app = Flask(__name__)





# configuring our flask app through the config object
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SUPABASE_URL")
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # optional but recommended
# access token
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET") 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
app.config["BUNDLE_ERRORS"] = True

# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
jwt = JWTManager(app)

bcrypt = Bcrypt(app)


# Initialize extensions
api = Api(app)
migrate = Migrate(app, db)
db.init_app(app)
CORS(app, resources={r"/*": {"origins": "*"}})
# CORS(app, resources={r"/admin/": {"origins": "http://localhost:5173"}})





# Register resource routes
api.add_resource(UserResources, "/user", "/user/<int:id>")
api.add_resource(LoginResource, "/login")
api.add_resource(ReportResource, "/reports", "/reports/<int:report_id>")
#api.add_resource(ReportResource, '/admin/reports', '/admin/reports/<int:id>')
api.add_resource(LocationResource, "/locations", "/locations/<int:location_id>")
# api.add_resource(ReportResource, "/admin/reports", "/admin/reports/<int:id>")
api.add_resource(ReportStatusUpdateResource, "/admin/reports/<int:report_id>/status")

# api.add_resource(ReportStatusUpdateResource,"/admin/reports" , "/admin/reports/<int:report_id>/status")


if __name__ == "__main__":
    app.run(debug=True)










