from datetime import datetime
from src import mongo_db

class VehicleDetails:

    def __init__(self, reg_no, owner_name, model, state, reg_type_descr, vehicle_class_desc, reg_upto, vehicle_pucc_details):
        self.reg_no = reg_no
        self.owner_name = owner_name
        self.model = model
        self.state = state
        self.reg_type_descr = reg_type_descr  # new field
        self.vehicle_class_desc = vehicle_class_desc  # new field
        self.reg_upto = reg_upto  # new field
        self.vehicle_pucc_details = vehicle_pucc_details

    def save_to_db(self):
        vehicles_collection = mongo_db.puc_info
        vehicle_data = {
            "reg_no": self.reg_no,
            "owner_name": self.owner_name,
            "model": self.model,
            "state": self.state,
            "reg_type_descr": self.reg_type_descr,  # new field
            "vehicle_class_desc": self.vehicle_class_desc,  # new field
            "reg_upto": self.reg_upto,  # new field
            "vehicle_pucc_details": self.vehicle_pucc_details,
        }
        result = vehicles_collection.insert_one(vehicle_data)
        return result.inserted_id
