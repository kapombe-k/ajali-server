from flask_restful import Resource, reqparse
import re
from datetime import datetime
from models import db, User, TokenBlocklist
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import (create_access_token, jwt_required, create_refresh_token, get_jwt_identity, get_jwt)
from flask import current_app

# class BaseResource(Resource):
#     def success_response(self, data, status=200):
#         return make_response(jsonify({
#             "status": "success",
#             "data": data
#         }), status)

#     def error_response(self, message, status=400):
#         return make_response(jsonify({
#             "status": "error",
#             "message": message
#         }), status)

class UserResources(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("first_name", type=str, required=True, help="first_name is required")
    parser.add_argument("last_name", type=str, required=True, help="last_name is required")
    parser.add_argument("email", type=str, required=True, help="Email is required")
    parser.add_argument("password", type=str, required=True)
    parser.add_argument("role", type=str, required=False, default='user')
    parser.add_argument("phone_number", type=str, required=True, help="phone_number is required")

    def validate_email(self, email):
        """Basic email format validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_password(self, password):
        """Password strength validation"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not any(char.isdigit() for char in password):
            return False, "Password must contain at least one digit"
        if not any(char.isupper() for char in password):
            return False, "Password must contain at least one uppercase letter"
        return True, "Password is valid"

    @jwt_required()
    def get(self, id=None):
        try:
            if id is None:
                users = User.query.all()
                return ({"Success": True, "data": [user.to_dict() for user in users]}), 200
            else:
                user = User.query.get(id)
                if not user:
                    return ({"Success": False, "message": "User not found"}), 404
                return ({"Success": True, "data": user.to_dict()}), 200
        except Exception as e:
            # Log the actual error for debugging but don't expose it to the client
            import logging
            logging.error(f"Error fetching user(s): {str(e)}")
            return ({"Success": False, "message": "An error occurred while fetching user data"}), 500

    def post(self):
        data = self.parser.parse_args()

        # Validate email format
        if not self.validate_email(data["email"]):
            return ({"Success": False, "message": "Invalid email format"}), 400
            
        # Validate password strength
        is_valid, message = self.validate_password(data["password"])
        if not is_valid:
            return ({"Success": False, "message": message}), 400
            
        # Check for existing email
        if User.query.filter_by(email=data["email"]).first():
            return ({"Success": False, "message": "Email address already taken"}), 409

        # Validate phone number format (exactly 10 digits)
        if not re.match(r'^\d{10}$', data["phone_number"]):
            return ({"Success": False, "message": "Phone number must be exactly 10 digits"}), 400

        # Check for existing phone number
        if User.query.filter_by(phone_number=data["phone_number"]).first():
            return ({"Success": False, "message": "Phone number already taken"}), 409

        try:
            # Hash password
            hashed_password = generate_password_hash(data['password']).decode('utf-8')
            data['password'] = hashed_password
            
            # Create user
            user = User(**data)
            db.session.add(user)
            db.session.commit()
            
            # Generate tokens
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={"name": user.first_name, "role": user.role}
            )
            refresh_token = create_refresh_token(
                identity=str(user.id),
                additional_claims={"name": user.first_name, "role": user.role}
            )
            
            return ({
                "Success": True,
                "data": {
                    "user": user.to_dict(),
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }
            }), 201

        except Exception as e:
            db.session.rollback()
            return ({"Success": False, "message": f"Error creating user: {str(e)}"}), 500

    @jwt_required()
    def patch(self, id):
        try:
            user = User.query.get(id)
            if not user:
                return ({"Success": False, "message": "User not found"}), 404

            data = self.parser.parse_args()

            if data['first_name'] is not None:
                user.first_name = data['first_name']
            if data['last_name'] is not None:
                user.last_name = data['last_name']
            if data['email'] is not None:
                user.email = data['email']
            if data['password'] is not None:
                user.password = generate_password_hash(data['password']).decode('utf-8')
            if data['phone_number'] is not None:
                user.phone_number = data['phone_number']

            db.session.commit()
            return (
                {"Success": True, "message": "User updated successfully", "data": user.to_dict()}
            ), 200
        except Exception as e:
            db.session.rollback()
            return ({"Success": False, "message": str(e)}), 500

    @jwt_required()
    def delete(self, id):
        try:
            user = User.query.get(id)
            if user is None:
                return ({"Success": False, "message": "User not found"}), 404

            db.session.delete(user)
            db.session.commit()
            return ({"Success": True, "message": "User successfully deleted"}), 200
        except Exception as e:
            db.session.rollback()
            return ({"Success": False, "message": str(e)}), 500

class LoginResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("email", type=str, required=True, help="Email is required")
    parser.add_argument("password", type=str, required=True, help="Password is required")

    # Apply rate limiting to this method
    def post(self):
        # Rate limit: 5 attempts per minute per IP
        # This would typically be handled by the Flask-Limiter extension
        # For now, we'll just add a comment about where this would be implemented
        
        try:
            data = self.parser.parse_args()
            user = User.query.filter_by(email=data["email"]).first()

            if not user or not check_password_hash(user.password, data['password']):
                # Use a generic message to prevent user enumeration attacks
                return ({"Success": False, "message": "Invalid credentials"}), 401

            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={"name": user.first_name, "role": user.role}
            )
            refresh_token = create_refresh_token(
                identity=str(user.id),
                additional_claims={"name": user.first_name, "role": user.role}
            )
            
            return ({
                "Success": True,
                "message": "Login successful",
                "data": {
                    "user": user.to_dict(),
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }
            }), 200
        except Exception as e:
            # Log the actual error for debugging but don't expose it to the client
            import logging
            logging.error(f"Error during login: {str(e)}")
            return ({"Success": False, "message": "An error occurred during login"}), 500

class TokenRefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return ({"Success": False, "message": "User not found"}), 404

            new_access_token = create_access_token(
                identity=str(user.id),
                additional_claims={"name": user.first_name, "role": user.role}
            )

            return ({
                "Success": True,
                "message": "Token refreshed successfully",
                "data": {
                    "access_token": new_access_token,
                    "user": user.to_dict()
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            return ({"Success": False, "message": str(e)}), 500


class LogoutResource(Resource):
    @jwt_required()
    def post(self):
        try:
            jti = get_jwt()["jti"]
            now = datetime.now()
            db.session.add(TokenBlocklist(jti=jti, created_at=now))
            db.session.commit()
            return {"Success": True, "message": "Successfully logged out"}, 200
        except Exception as e:
            db.session.rollback()
            return {"Success": False, "message": f"Error during logout: {str(e)}"}, 500