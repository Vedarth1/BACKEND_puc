from src import mongo_db

class User:
    def __init__(self, username, email, password, user_type):
        self.username = username
        self.email = email
        self.password = password
        self.user_type = user_type

    def save(self):
        users_collection = mongo_db.users
        user_data = {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "user_type": self.user_type
        }
        users_collection.insert_one(user_data)