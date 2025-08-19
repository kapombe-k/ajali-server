
import os
from datetime import timedelta
from dotenv import load_dotenv

# Flask imports
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

#resource imports
from models import db, TokenBlocklist
from resources.user import UserResources, LoginResource, TokenRefreshResource
from resources.status_update import ReportStatusUpdateResource
from resources.emergency_contact import EmergencyContactResource
from resources.report import ReportResource
from resources.location import LocationResource
from resources.adminResource import AdminResource
from resources.user import LogoutResource
from resources.report import MediaResource

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
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_COOKIE_CSRF_PROTECT"] = True
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
app.config["BUNDLE_ERRORS"] = True

# Initialize extensions
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
api = Api(app)
migrate = Migrate(app, db)
db.init_app(app)

#Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"]
)

# JWT token revocation callback
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None

# Callback function for expired tokens
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {"Success": False, "message": "Token has expired"}, 401

# Callback function for invalid tokens
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {"Success": False, "message": f"Invalid token: {error}"}, 401

# Callback function for revoked tokens
@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return {"Success": False, "message": "Token has been revoked"}, 401

# CORS Configuration
BASE_URL = os.environ.get("BASE_URL")

# CORS setup with proper credentials support
CORS(
    app,
    resources={r"/*": {"origins": BASE_URL}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
)

# Resource routes
api.add_resource(UserResources, "/users", "/users/<int:id>")
api.add_resource(LoginResource, "/login")
api.add_resource(TokenRefreshResource, "/token/refresh")
api.add_resource(LogoutResource, "/logout")
api.add_resource(ReportResource, "/reports", "/reports/<int:report_id>")
api.add_resource(MediaResource, "/reports/<int:report_id>/media")
api.add_resource(LocationResource, "/locations", "/locations/<int:location_id>")
api.add_resource(EmergencyContactResource, "/emergency-contacts", "/emergency-contacts/<int:id>")
api.add_resource(AdminResource, "/admin/reports", "/admin/reports/<int:report_id>")
api.add_resource(ReportStatusUpdateResource, "/reports/<int:report_id>/status")

@app.after_request
def after_request(response):
    # CORS headers
    response.headers.add('Access-Control-Allow-Origin')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-CSRF-Token')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response


if __name__ == "__main__":
    app.run()