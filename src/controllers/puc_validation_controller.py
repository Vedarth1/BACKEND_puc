from flask import request, Response, json, Blueprint
from datetime import datetime  # Import datetime to get the current date
from src.services.validation_service import perform_puc_validation
from src.models.puc_info import VehicleDetails
from src import mongo_db
from flask_cors import CORS

puc_validation = Blueprint("puc_validation", __name__)

CORS(puc_validation)

@puc_validation.route('/puc_status', methods=["POST"])
def check_puc_validation():
    try:
        data = request.json
        if "rc_number" not in data:
            return Response(
                response=json.dumps({'status': "failed", "message": "RC number is required"}),
                status=400,
                mimetype='application/json'
            )
        
        vehiclecollections = mongo_db.puc_info
        existing_vehicle = vehiclecollections.find_one({"reg_no": data["rc_number"]})
        
        if existing_vehicle:
            message = ""
            vehicle_pucc_details = existing_vehicle.get("vehicle_pucc_details")
            if vehicle_pucc_details is not None:
                message = "PUC is Valid!!"
            else:
                message = "PUC is Invalid!!"

            formatted_data = {
                "message": message,
                "reg_no": existing_vehicle.get("reg_no"),
                "owner_name": existing_vehicle.get("owner_name"),
                "model": existing_vehicle.get("model"),
                "state": existing_vehicle.get("state"),
                "reg_type_descr": existing_vehicle.get("reg_type_descr"),  # new field
                "vehicle_class_desc": existing_vehicle.get("vehicle_class_desc"),  # new field
                "reg_upto": existing_vehicle.get("reg_upto"),  # new field
                "vehicle_pucc_details": vehicle_pucc_details,
                "checked_on": existing_vehicle.get("checked_on", datetime.now().strftime('%Y-%m-%d'))  # Use existing checked_on or set current date
            }
            return Response(
                response=json.dumps(formatted_data),
                status=200,
                mimetype='application/json'
            )
        
        # If vehicle not found in local database, perform external validation
        rto_response = perform_puc_validation(data["rc_number"])
        print(rto_response)

        if "error" in rto_response:
            error_message = rto_response["error"]
            print("error_message", error_message)
            return Response(
                response=json.dumps({'status': "failed", "message": f"Validation Error: {error_message}"}),
                status=400,
                mimetype='application/json'
            )

        message = ""
        vehicle_pucc_details = rto_response["result"].get("vehicle_pucc_details")
        if vehicle_pucc_details is not None:
            message = "PUC is Valid!!"
        else:
            message = "PUC is Invalid!!"

        # Add checked_on to the formatted data
        checked_on = datetime.now().strftime('%Y-%m-%d')
        formatted_data = {
            "message": message,
            "reg_no": rto_response["result"]["reg_no"],
            "owner_name": rto_response["result"]["owner_name"],
            "model": rto_response["result"]["model"],
            "state": rto_response["result"]["state"],
            "reg_type_descr": rto_response["result"]["reg_type_descr"],  # new field
            "vehicle_class_desc": rto_response["result"]["vehicle_class_desc"],  # new field
            "reg_upto": rto_response["result"]["reg_upto"],  # new field
            "vehicle_pucc_details": vehicle_pucc_details,
            "checked_on": checked_on  # Set the checked_on date
        }

        print("Saving in db!!")
        vehicle_details = VehicleDetails(
            reg_no=formatted_data["reg_no"],
            owner_name=formatted_data["owner_name"],
            model=formatted_data["model"],
            state=formatted_data["state"],
            reg_type_descr=formatted_data["reg_type_descr"],  # new field
            vehicle_class_desc=formatted_data["vehicle_class_desc"],  # new field
            reg_upto=formatted_data["reg_upto"],  # new field
            vehicle_pucc_details=formatted_data["vehicle_pucc_details"],
            checked_on=checked_on  # Save the checked_on date to the database
        )

        vehicle_details.save_to_db()

        return Response(
            response=json.dumps(formatted_data),
            status=200,
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
