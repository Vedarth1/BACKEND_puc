from datetime import datetime
from src import mongo_db

class VehicleDetails:

    def __init__(self, rc_number, pucc_details):
        self.rc_number = rc_number
        self.pucc_details = self.validate_pucc_details(pucc_details)

    def validate_pucc_details(self, pucc_details):
        required_keys = {"pucc_from", "pucc_upto", "pucc_centreno", "pucc_no", "op_dt"}
        if not required_keys.issubset(pucc_details.keys()):
            raise ValueError("Missing required keys in PUC details")

        # You can add additional validation logic here for specific formats (e.g., date format)

        return pucc_details

    def get_formatted_pucc_expiry(self):
        try:
            pucc_upto = datetime.strptime(self.pucc_details["pucc_upto"], "%d-%m-%Y")
            return pucc_upto.strftime("%Y-%m-%d")
        except ValueError:
            return None



    def save_to_db(self):
        vehicles_collection=mongo_db.puc_info
        vehicle_data = {
            "rc_number": self.rc_number,
            "pucc_details": self.pucc_details,
        }
        result = vehicles_collection.insert_one(vehicle_data)
        return result.inserted_id
