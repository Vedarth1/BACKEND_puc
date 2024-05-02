from datetime import datetime
from src import mongo_db

class VehicleDetails:

    def __init__(self, reg_no, owner_name, model, state, vehicle_pucc_details):
        self.reg_no = reg_no
        self.owner_name = owner_name
        self.model = model
        self.state = state
        self.vehicle_pucc_details = vehicle_pucc_details

    def save_to_db(self):
        vehicles_collection = mongo_db.puc_info
        vehicle_data = {
            "reg_no": self.reg_no,
            "owner_name": self.owner_name,
            "model": self.model,
            "state": self.state,
            "vehicle_pucc_details": self.vehicle_pucc_details,
        }
        result = vehicles_collection.insert_one(vehicle_data)
        return result.inserted_id
