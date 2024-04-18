from src import mongo_db

class User:
    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password

    def save(self):
        # Assuming you have a users collection in your MongoDB database
        users_collection = mongo_db.users
        user_data = {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "password": self.password
        }
        users_collection.insert_one(user_data)

    @staticmethod
    def find_by_email(email):
        users_collection = mongo_db.users
        user_data = users_collection.find_one({"email": email})
        if user_data:
            return User(
                user_data["firstname"],
                user_data["lastname"],
                user_data["email"],
                user_data["password"]
            )
        return None
