import requests
from flask import request, Response, json, Blueprint
from src import mongo_db
from src.models.puc_info import VehicleDetails

puc_validation = Blueprint("puc_validation", __name__)

RAPID_API_URL = "https://rto-vehicle-information-verification-india.p.rapidapi.com/api/v1/rc/vehicleinfo"
RAPID_API_HEADERS = {
    'content-type': 'application/json',
    'X-RapidAPI-Key': '7f86c5e89emshb565944abf4725bp128325jsnd9462a2ea579',
    'X-RapidAPI-Host': 'rto-vehicle-information-verification-india.p.rapidapi.com'
}


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
        
        vehicles_collection = mongo_db.puc_info
        vehicle_data = vehicles_collection.find_one({"rc_number": data["rc_number"]})
        if vehicle_data:
            return Response(
                response=json.dumps({'status': "success",
                                     "message": "PUC validation already performed",
                                     'vehicle_data': vehicle_data}),
                status=200,
                mimetype='application/json'
            )
        else:
            payload = {
                "reg_no": data["rc_number"],
                "consent": "Y",
                "consent_text": "I hear by declare my consent agreement for fetching my information via AITAN Labs API"
            }
            response = requests.post(RAPID_API_URL, json=payload, headers=RAPID_API_HEADERS)
            print(response)
            if response.status_code == 200:
                puc_data = response.json()
                print(puc_data)
                vehicle_puc_details = puc_data["result"].get("vehicle_pucc_details", {})
                print(vehicle_puc_details)

                if vehicle_puc_details:
                    vehicle_details = VehicleDetails(data["rc_number"], vehicle_puc_details)
                    vehicle_details.save_to_db()
                    
                    return Response(json.dumps({
                        'status': "success",
                        'message': "PUC is valid!!",
                        'vehicle_data': vehicle_puc_details
                    }), status=200, mimetype='application/json')
                else:
                    return Response(json.dumps({
                        'status': "success",
                        'message': "PUC is invalid!!",
                        'vehicle_data': vehicle_puc_details
                    }), status=200, mimetype='application/json')
            else:
                return Response(json.dumps({
                    'status': "failed",
                    'message': "Failed to perform PUC validation",
                    'error': response.json()
                }), status=response.status_code, mimetype='application/json')
        
    except Exception as e:
        print(e)
        return Response(
            response=json.dumps({'status': "failed",
                                 "message": "Error Occurred",
                                 "error": str(e)}),
            status=500,
            mimetype='application/json'
        )    
