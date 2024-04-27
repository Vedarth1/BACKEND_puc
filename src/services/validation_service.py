import requests
from src import mongo_db
from src.models.puc_info import VehicleDetails

RAPID_API_URL = "https://rto-vehicle-information-verification-india.p.rapidapi.com/api/v1/rc/vehicleinfo"
RAPID_API_HEADERS = {
    'content-type': 'application/json',
    'X-RapidAPI-Key': '6a8afe9103msh9d6fe6d5f3a7ab7p1ec95cjsn3e90a405a0cc',
    'X-RapidAPI-Host': 'rto-vehicle-information-verification-india.p.rapidapi.com'
}

def perform_puc_validation(rc_number):
    try:
        vehicles_collection = mongo_db.puc_info
        vehicle_data = vehicles_collection.find_one({"rc_number": rc_number})
        if vehicle_data:
            return {
                'status': "success",
                "message": "PUC validation already performed",
                'vehicle_data': vehicle_data
            }
        else:
            payload = {
                "reg_no": rc_number,
                "consent": "Y",
                "consent_text": "I hereby declare my consent agreement for fetching my information via AITAN Labs API"
            }
            response = requests.post(RAPID_API_URL, json=payload, headers=RAPID_API_HEADERS)
            if response.status_code == 200:
                puc_data = response.json()
                vehicle_puc_details = puc_data["result"].get("vehicle_pucc_details", {})
                if vehicle_puc_details:
                    vehicle_details = VehicleDetails(rc_number, vehicle_puc_details)
                    vehicle_details.save_to_db()
                    return {
                        'status': "success",
                        'message': "PUC is valid!!",
                        'vehicle_data': vehicle_puc_details
                    }
                else:
                    return {
                        'status': "success",
                        'message': "PUC is invalid!!",
                        'vehicle_data': vehicle_puc_details
                    }
            else:
                return {
                    'status': "failed",
                    'message': "Failed to perform PUC validation",
                    'error': response.json()
                }
        
    except Exception as e:
        return {
            'status': "failed",
            "message": "Error Occurred",
            "error": str(e)
        }
