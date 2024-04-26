import jwt
import os
from datetime import datetime
from bson import ObjectId

def generate_token(user_id, user_data):
    payload = {
        'iat': datetime.utcnow(),
        'user_id': str(user_id),
        'username': user_data["username"],  # Update to use "username" instead of "firstname" and "lastname"
        'email': user_data["email"],
        'user_type': user_data.get("user_type")  # Include user type in the payload
    }
    token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')
    return token
