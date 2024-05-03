import requests

RAPID_API_URL = "https://rto-vehicle-information-verification-india.p.rapidapi.com/api/v1/rc/vehicleinfo"
RAPID_API_HEADERS = {
    'content-type': 'application/json',
    'X-RapidAPI-Key': '2c328b0865msh5231be45032bfdbp11fa6djsn6969dbbad1b3',
    'X-RapidAPI-Host': 'rto-vehicle-information-verification-india.p.rapidapi.com'
}

def perform_puc_validation(rc_number):
    try:
        payload = {
            "reg_no": rc_number,
            "consent": "Y",
            "consent_text": "I hereby declare my consent agreement for fetching my information via AITAN Labs API"
        }
        response = requests.post(RAPID_API_URL, json=payload, headers=RAPID_API_HEADERS)
        if response.status_code == 200:
            puc_data = response.json()
            return puc_data
        else:
            return {
                "error": response.json()
            }
    except Exception as e:
        return {
            "error": str(e)
        }
