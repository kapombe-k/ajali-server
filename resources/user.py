
from flask_restful import Resource,reqparse
import re
from models import db,User
from flask_bcrypt import generate_password_hash,check_password_hash
from flask_jwt_extended import  create_access_token, jwt_required, create_refresh_token, get_jwt_identity

class UserResources(Resource):
    parser =reqparse.RequestParser()
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
    def get(self,id=None):
        if id is None:
            users= User.query.all()
            return[user.to_dict() for user in users],200
        else:
            user =User.query.filter_by(id=id).first()
            if user is None:
                return {"message":"User not Found"},404
        return user.to_dict(),200
    
    def post(self):
        data = self.parser.parse_args()

        # Validate email format
        if not self.validate_email(data["email"]):
            return {"message": "Invalid email format"}, 400
            
        # Validate password strength
        is_valid, message = self.validate_password(data["password"])
        if not is_valid:
            return {"message": message}, 400
            
        # Check for existing email
        if User.query.filter_by(email=data["email"]).first():
            return {"message": "Email address already taken"}, 409
            
        # Check for existing phone number
        if User.query.filter_by(phone_number=data["phone_number"]).first():
            return {"message": "Phone number already taken"}, 409
            
        # Hash password
        hashed_password = generate_password_hash(data['password']).decode('utf-8')
        data['password'] = hashed_password
        
        # Create user
        try:
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
            
            response = {
                "message": "User registered successfully",
                "user": user.to_dict(),
                "access_token": access_token,
                "refresh_token": refresh_token
            }
            return response, 201
            
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error creating user: {str(e)}"}, 500
    
    @jwt_required()
    def patch(self,id):
        user=User.query.filter_by(id=id).first()
        if not user:
            return{"message":"User not found"},404
        
        data =self.parser.parse_args()

        if data['first_name'] is not None:
            user.first_name=data['first_name']
        if data['last_name'] is not None:
            user.last_name =data['last_name']
        if data ['email'] is not None:
            user.email=data['email']
        if data ['password'] is not None:
            user.password =data['password']
        if data ['phone_number'] is not None:
            user.phone_number =data['phone_number']

        db.session.commit()

        return {"message":"User updated sucessfully","user":user.to_dict()},201

    @jwt_required()
    def delete(self,id):
        # Fetch user by ID
        user =User.query.filter_by(id=id).first()  
        if user is None:
            # if user does not exist
            return{"message":"User not found"},404
        db.session.delete(user)
        db.session.commit()
        return{"message":"User sucessfully deleted"},202

        
class LoginResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("email", type=str, required=True, help="Email is required")
    parser.add_argument("password", type=str, required=True, help="Password is required")

    def post(self):
        # Handle user login
        data = self.parser.parse_args()
        user = User.query.filter_by(email=data["email"]).first()

        if not user or not check_password_hash(user.password, data['password']):
            return {"message": "Incorrect email or password"}, 401
            
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"name": user.first_name, "role": user.role}
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={"name": user.first_name, "role": user.role}
        )
        
        response = {
            "message": "Login successful",
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        return response, 200
    
class TokenRefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        user = User.query.get(current_user)
        
        if not user:
            return {"message": "User not found"}, 404
            
        new_access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"name": user.first_name, "role": user.role}
        )
        
        return {
            "access_token": new_access_token,
            "user": user.to_dict()
        }, 200




 