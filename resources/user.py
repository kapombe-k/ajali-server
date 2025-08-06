
from flask_restful import Resource,reqparse

from models import db,User
from flask_bcrypt import generate_password_hash,check_password_hash
from flask_jwt_extended import  create_access_token


class UserResources(Resource):
    parser =reqparse.RequestParser()
    parser.add_argument("first_name", type=str, required=True, help="first_name is required")
    parser.add_argument("last_name", type=str, required=True, help="last_name is required")
    parser.add_argument("email", type=str, required=True, help="Email is required")
    parser.add_argument("password", type=str, required=True)
    parser.add_argument("role", type=str, required=False)
    parser.add_argument("phone_number", type=str, required=True, help="phone_number is required")

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
        # step.1 check for uniqueness in both email and phone_number
        email =User.query.filter_by(email=data["email"]).first()
        if email:
            return{"message":"Email Address already taken"}
        
        phone_number=User.query.filter_by(phone_number=data["phone_number"]).first()

        if phone_number:
            return {"message":"phone_number already taken"}
        # step 2.encrypt the password
        hash = generate_password_hash(data['password']).decode('utf-8')
        # step.3 save users info
        data['password'] = hash
        user_data =User(**data)
        db.session.add(user_data)
        db. session.commit()
        return {"message":"User added sucessfully"},201
    
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
        if user is None:
            return{"message":"incorrect email address or password"}, 401

        if check_password_hash(user.password,data['password']):
            access_token=create_access_token( identity=str(user.id), additional_claims={"name": user.first_name, "role": user.role})
            # For hashed passwords
            # if not user or not check_password_hash(user.password, data["password"]):
            return {"message": "Login successful", "user":user.to_dict(), "acess_token": access_token}, 200
        else:
            return{"message":"incorrect email or password"},401




 