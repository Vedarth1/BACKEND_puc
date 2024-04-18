import jwt,os
from flask import request, Response, json, Blueprint
from src.models.user_model import User
from src import mongo_db
from src.services.jwt_service import generate_token
from src.library.hashing import hash_password, check_password_hash

# user controller blueprint to be registered with api blueprint
users = Blueprint("users", __name__)

# route for login api/users/signin
@users.route('/login', methods = ["POST"])
def handle_login():
    try: 
        # first check user parameters
        data = request.json
        if "email" and "password" in data:
            # check db for user records
            users_collection = mongo_db.users
            user_data = users_collection.find_one({"email": data["email"]})

            # if user records exists we will check user password
            if user_data:
                # check user password
                if check_password_hash(user_data["password"], data["password"]):
                    # User password matched, generate token
                    token = generate_token(user_data["_id"],user_data)
                    return Response(
                        response=json.dumps({'status': "success",
                                             "message": "User LogIn Successful",
                                             "token": token}),
                        status=200,
                        mimetype='application/json'
                    )
                else:
                    return Response(
                        response=json.dumps({'status': "failed", "message": "User Password Mismatched"}),
                        status=401,
                        mimetype='application/json'
                    )
            # If there is no user record
            else:
                return Response(
                    response=json.dumps({'status': "failed", "message": "User Record doesn't exist, kindly register"}),
                    status=404,
                    mimetype='application/json'
                )
        else:
            # If request parameters are not correct
            return Response(
                response=json.dumps({'status': "failed", "message": "User Parameters Email and Password are required"}),
                status=400,
                mimetype='application/json'
            )

    except Exception as e:
        return Response(
            response=json.dumps({'status': "failed",
                                 "message": "Error Occurred",
                                 "error": str(e)}),
            status=500,
            mimetype='application/json'
        )



# route for login api/users/signup
@users.route('/signup', methods = ["POST"])
def handle_signup():
    try:
        # First validate required user parameters
        data = request.json
        if "firstname" in data and "lastname" in data and "email" in data and "password" in data:
            # Validate if the user exists
            users_collection = mongo_db.users
            existing_user = users_collection.find_one({"email": data["email"]})

            # If the user doesn't exist
            if not existing_user:
                # Hash the password
                hashed_password = hash_password(data['password'])

                # Create user data
                user_data = {
                    "firstname": data["firstname"],
                    "lastname": data["lastname"],
                    "email": data["email"],
                    "password": hashed_password
                }

                # Insert user data into the database
                inserted_user = users_collection.insert_one(user_data)
                print(inserted_user)
                token = generate_token(inserted_user.inserted_id,user_data)
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
            # If request parameters are not correct
            return Response(
                response=json.dumps({'status': "failed",
                                     "message": "User Parameters Firstname, Lastname, Email and Password are required"}),
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