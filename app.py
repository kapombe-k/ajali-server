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
from resources.user import UserResources, LoginResource, TokenRefreshResource
from resources.status_update import ReportStatusUpdateResource
from resources.report import ReportResource
from resources.location import LocationResource


# import the configs stored inside the env file
load_dotenv()

app = Flask(__name__)

# configuring our flask app through the config object
#app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SUPABASE_URL")
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# access token and JWT configuration
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET") 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]  # Enable JWT in cookies
app.config["JWT_COOKIE_SECURE"] = True  # Only send over HTTPS
app.config["JWT_COOKIE_CSRF_PROTECT"] = True  # Enable CSRF protection
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
app.config["BUNDLE_ERRORS"] = True

# Initialize extensions
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
api = Api(app)
migrate = Migrate(app, db)
db.init_app(app)

# CORS Configuration
FRONTEND_URL = os.environ.get("FRONTEND_URL")
app.config["CORS_SUPPORTS_CREDENTIALS"] = True
app.config["CORS_ORIGINS"] = [FRONTEND_URL]

# CORS setup with proper credentials support
CORS(
    app,
    resources={r"/*": {"origins": FRONTEND_URL}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
)

# Register resource routes
api.add_resource(UserResources, "/users", "/users/<int:id>")
api.add_resource(LoginResource, "/login")
api.add_resource(TokenRefreshResource, "/token/refresh")
api.add_resource(ReportResource, "/reports", "/reports/<int:report_id>")
api.add_resource(LocationResource, "/locations", "/locations/<int:location_id>")
api.add_resource(ReportStatusUpdateResource, "/reports/<int:report_id>/status")

@app.after_request
def after_request(response):
    # Ensure responses have proper CORS headers
    response.headers.add('Access-Control-Allow-Origin', FRONTEND_URL)
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == "__main__":
    app.run()