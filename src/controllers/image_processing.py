import requests
import os
import zipfile
import shutil
from io import BytesIO
from PIL import Image
from flask import request, Response, json, Blueprint
from werkzeug.utils import secure_filename
from src.services.parsing_service import parse_rc_number
from src.services.validation_service import perform_puc_validation
from src.models.puc_info import VehicleDetails
from flask_cors import CORS
from flask_socketio import emit
from src import socketio, mongo_db


image_processing = Blueprint("image_processing", __name__)
CORS(image_processing)

@image_processing.route('/process_image', methods=["POST"])
def process_image():
    try:
        if 'file' not in request.files:
            raise ValueError("File not found")
        
        file = request.files['file']

        if file.filename == '':
            raise ValueError("File not found")
        
        URL = "http://20.198.19.131:5000/predict" 
        files = {'file': (file.filename, file, file.content_type)}
        
        Apiresponse = requests.post(URL, files=files)

        # Ensure the response contains a ZIP file
        if 'application/zip' not in Apiresponse.headers.get('Content-Type'):
            raise ValueError("Expected a zip file in the API response.")

        zip_file = BytesIO(Apiresponse.content)  # Store zip file in memory

        # Unzipping the file
        image_dir = os.path.join(os.getcwd(), 'image_dir')
        os.makedirs(image_dir, exist_ok=True)

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(image_dir)

        headers = {
            'X-RapidAPI-Key': "edf168fcb4mshef0502ef2b445e6p1cd6d7jsn34d9a4bd9305",
            'X-RapidAPI-Host': 'ocr43.p.rapidapi.com'
        }

        image_processed_data = []

        for filename in os.listdir(image_dir):
            file_path = os.path.join(image_dir, filename)

            image = Image.open(file_path).convert("RGB")
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            form_data = {
                'image': ('image.jpg', img_byte_arr)
            }

            response = requests.post('https://ocr43.p.rapidapi.com/v1/results', headers=headers, files=form_data)
            
            if response.status_code != 200:
                socketio.emit('puc_validation_error', {'error': f"Failed to perform OCR: {response.json()}"})
                return Response(json.dumps({
                    'status': "failed",
                    'message': "Failed to perform OCR",
                    'error': response.json()
                }), status=response.status_code, mimetype='application/json')

            ocr_response = response.json()
            text = ocr_response['results'][0]['entities'][0]['objects'][0]['entities'][0]['text']
            image_processed_data.append(text)

            try:
                os.remove(file_path)
            except Exception as e:
                socketio.emit('puc_validation_error', {'error': f"Error in removing temporary file: {str(e)}"})
                return Response(
                    response=json.dumps({'status': "failed",
                                         "message": "Error in removing the temporary file",
                                         "error": str(e)}),
                    status=500,
                    mimetype='application/json'
                )
            
        image_processed_data = parse_rc_number(image_processed_data)

        result_rto_info = []

        for rc_number in image_processed_data:
            vehiclecollections = mongo_db.puc_info
            existing_vehicle = vehiclecollections.find_one({"reg_no": rc_number})

            if existing_vehicle:
                vehicle_pucc_details = existing_vehicle.get("vehicle_pucc_details")
                message = "PUC is Valid!!" if vehicle_pucc_details else "PUC is Invalid!!"

                formatted_data = {
                    "message": message,
                    "reg_no": existing_vehicle.get("reg_no"),
                    "owner_name": existing_vehicle.get("owner_name"),
                    "model": existing_vehicle.get("model"),
                    "state": existing_vehicle.get("state"),
                    "reg_type_descr": existing_vehicle.get("reg_type_descr"),
                    "vehicle_class_desc": existing_vehicle.get("vehicle_class_desc"),
                    "reg_upto": existing_vehicle.get("reg_upto"),
                    "vehicle_pucc_details": vehicle_pucc_details
                }

                result_rto_info.append(formatted_data)
                continue

            rto_response = perform_puc_validation(rc_number)
            if "error" in rto_response:
                error_message = rto_response["error"]
                socketio.emit('puc_validation_error', {'error': f"Validation Error: {error_message}"})
                return Response(
                    response=json.dumps({'status': "failed", "message": f"Validation Error: {error_message}"}),
                    status=400,
                    mimetype='application/json'
                )

            message = "PUC is Valid!!" if rto_response["result"]["vehicle_pucc_details"] else "PUC is Invalid!!"
            
            formatted_data = {
                "message": message,
                "reg_no": rto_response["result"]["reg_no"],
                "owner_name": rto_response["result"]["owner_name"],
                "model": rto_response["result"]["model"],
                "state": rto_response["result"]["state"],
                "reg_type_descr": rto_response["result"]["reg_type_descr"],
                "vehicle_class_desc": rto_response["result"]["vehicle_class_desc"],
                "reg_upto": rto_response["result"]["reg_upto"],
                "vehicle_pucc_details": rto_response["result"]["vehicle_pucc_details"]
            }

            vehicle_details = VehicleDetails(
                reg_no=formatted_data["reg_no"],
                owner_name=formatted_data["owner_name"],
                model=formatted_data["model"],
                state=formatted_data["state"],
                reg_type_descr=formatted_data["reg_type_descr"],
                vehicle_class_desc=formatted_data["vehicle_class_desc"],
                reg_upto=formatted_data["reg_upto"],
                vehicle_pucc_details=formatted_data["vehicle_pucc_details"]
            )
            vehicle_details.save_to_db()

            result_rto_info.append(formatted_data)

        # Emit the result_rto_info through WebSocket
        socketio.emit('puc_validation_result', {'data': result_rto_info})

        return Response(json.dumps({
            'status': "success",
            'message': "Image processing done successfully",
            'response': result_rto_info
        }), status=200, mimetype='application/json')

    except Exception as e:
        error_message = str(e)
        socketio.emit('puc_validation_error', {'error': error_message})
        return Response(
            response=json.dumps({'status': "failed", "message": "Error Occurred", "error": error_message}),
            status=500,
            mimetype='application/json'
        )
    finally:
        image_dir = os.path.join(os.getcwd(), 'image_dir')
        if os.path.exists(image_dir):
            try:
                shutil.rmtree(image_dir)  # This removes the directory and all its contents
                print(f"{image_dir} has been removed successfully.")
            except Exception as e:
                print(f"Failed to remove {image_dir}. Error: {str(e)}")