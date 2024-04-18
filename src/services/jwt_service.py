import jwt
import os
from datetime import datetime
from bson import ObjectId

def generate_token(user_id,user_data):

    payload = {
        'iat': datetime.utcnow(),
        'user_id': str(user_id),
        'firstname': user_data["firstname"],
        'lastname': user_data["lastname"],
        'email': user_data["email"],
    }
    token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')
    return token
