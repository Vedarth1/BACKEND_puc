import jwt,os
from flask import request, Response, json, Blueprint
from src.models.user_model import User
from src import mongo_db
from src.services.jwt_service import generate_token
from src.library.hashing import hash_password, check_password_hash
from flask_cors import CORS
# user controller blueprint to be registered with api blueprint
users = Blueprint("users", __name__)
CORS(users)

# route for login api/users/signin
@users.route('/login', methods=["POST"])
def handle_login():
    try:
        data = request.json
        if "email" in data and "password" in data and "user_type" in data:
            # Check database for user records based on user_type
            users_collection = mongo_db.users
            user_data = users_collection.find_one({"email": data["email"], "user_type": data["user_type"]})

            # If user records exist, check user password
            if user_data:
                # Check user password
                if check_password_hash(user_data["password"], data["password"]):
                    # User password matched, generate token
                    token = generate_token(user_data["_id"], user_data)
                    return Response(
                        response=json.dumps({'status': "success",
                                             "message": "User LogIn Successful",
                                             "token": token}),
                        status=200,
                        mimetype='application/json'
                    )
                else:
                    # Password mismatch
                    return Response(
                        response=json.dumps({'status': "failed", "message": "User Password Mismatched"}),
                        status=401,
                        mimetype='application/json'
                    )
            else:
                # User record doesn't exist
                return Response(
                    response=json.dumps({'status': "failed", "message": "User Record doesn't exist, kindly register"}),
                    status=404,
                    mimetype='application/json'
                )
        else:
            # Incorrect request parameters
            return Response(
                response=json.dumps({'status': "failed", "message": "User Parameters Email, Password, and User Type are required"}),
                status=400,
                mimetype='application/json'
            )

    except Exception as e:
        # Error occurred
        return Response(
            response=json.dumps({'status': "failed",
                                 "message": "Error Occurred",
                                 "error": str(e)}),
            status=500,
            mimetype='application/json'
        )


# route for login api/users/signup
@users.route('/signup', methods=["POST"])
def handle_signup():
    try:
        # First validate required user parameters
        data = request.json
        if "username" in data and "email" in data and "password" in data and "confirm_password" in data and "user_type" in data:
            # Check if password matches confirm_password
            if data["password"] == data["confirm_password"]:
                # Validate if the user exists
                users_collection = mongo_db.users
                existing_user = users_collection.find_one({"email": data["email"]})

                # If the user doesn't exist
                if not existing_user:
                    # Hash the password
                    hashed_password = hash_password(data['password'])

                    # Create user data
                    user_data = {
                        "username": data["username"],
                        "email": data["email"],
                        "password": hashed_password,
                        "user_type": data["user_type"]  # Add user type to user data
                    }

                    # Insert user data into the database
                    inserted_user = users_collection.insert_one(user_data)
                    token = generate_token(inserted_user.inserted_id, user_data)
                    return Response(
                        response=json.dumps({'status': "success",
                                             "message": "User Sign up Successful",
                                             "token": token}),
                        status=201,
                        mimetype='application/json'
                    )
                else:
                    # If user already exists
                    return Response(
                        response=json.dumps({'status': "failed", "message": "User already exists, kindly sign in"}),
                        status=409,
                        mimetype='application/json'
                    )
            else:
                # If password and confirm_password do not match
                return Response(
                    response=json.dumps({'status': "failed",
                                         "message": "Password and Confirm Password do not match"}),
                    status=400,
                    mimetype='application/json'
                )
        else:
            # If request parameters are not correct
            return Response(
                response=json.dumps({'status': "failed",
                                     "message": "User Parameters Username, Email, Password, Confirm Password, and User Type are required"}),
                status=400,
                mimetype='application/json'
            )

    except Exception as e:
        print(e)
        return Response(
            response=json.dumps({'status': "failed",
                                 "message": "Error Occurred",
                                 "error": str(e)}),
            status=500,
            mimetype='application/json'
        )