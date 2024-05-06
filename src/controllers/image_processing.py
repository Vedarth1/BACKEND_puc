import requests
import os
import subprocess
from io import BytesIO
from PIL import Image
from flask import request, Response, json, Blueprint
from werkzeug.utils import secure_filename
from src.services.parsing_service import parse_rc_number
from src.services.validation_service import perform_puc_validation
from src.models.puc_info import VehicleDetails
from src import mongo_db
import os

image_processing = Blueprint("image_processing", __name__)

@image_processing.route('/process_image',methods=["POST"])
def process_image():
    try:
        if 'file' not in request.files:
            return Response(
                response=json.dumps({'error': 'No file uploaded'}),
                status=400,
                mimetype='application/json'
            )
        
        file = request.files['file']

        if file.filename == '':
            return Response(
                response=json.dumps({'error': 'Empty file uploaded'}),
                status=400,
                mimetype='application/json'
            )
        
        filename = secure_filename(file.filename)
        
        # Set the file extension to ".jpg"
        filename_with_extension = filename.rsplit('.', 1)[0] + '.jpg'

        # Create a temporary directory if it doesn't exist
        temp_dir = os.path.join(os.getcwd(), 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Save the file to the temporary directory
        temp_file_path = os.path.join(temp_dir, filename_with_extension)
        file.save(temp_file_path)

        print("File received!!! \n Model is working on image!")

        command = f"python Detection-model/ultralytics/yolo/v8/detect/predict.py model='Detection-model/newpts.pt' source=\"{temp_file_path}\""

        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            return Response(json.dumps({
                'status': "failed",
                'message': "Model finds an error while processing",
                'error': str(e)
            }), status=500, mimetype='application/json')
        
        print("image processed by model")

        # Remove the temporary file
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except Exception as e:
            return Response(
                response=json.dumps({'status': "failed",
                                    "message": "Error in removing the temporary file",
                                    "error": str(e)}),
                status=500,
                mimetype='application/json'
            )

        print("performing ocr")

        image_dir = os.path.dirname(__file__)
        while not os.path.isfile(os.path.join(image_dir, 'requirements.txt')):
            image_dir = os.path.dirname(image_dir)
        image_dir+='/results'

        headers = {
            'X-RapidAPI-Key': os.getenv("RAPID_API_OCR_KEY"),
            'X-RapidAPI-Host': 'ocr43.p.rapidapi.com'
        }

        image_processed_data=[]

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
            ocr_response=response.json()
            print(ocr_response)

            text=ocr_response['results'][0]['entities'][0]['objects'][0]['entities'][0]['text']
            if response.status_code == 200:
                image_processed_data.append(text)
            else:
                return Response(json.dumps({
                    'status': "failed",
                    'message': "Failed to perform OCR",
                    'error': response.json()
                }), status=response.status_code, mimetype='application/json')
            
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                return Response(
                    response=json.dumps({'status': "failed",
                                        "message": "Error in remove the temporary file",
                                        "error": str(e)}),
                    status=500,
                    mimetype='application/json'
                )
            
        image_processed_data=parse_rc_number(image_processed_data)

        print(image_processed_data)

        result_rto_info=[]

        for rc_number in image_processed_data:

            vehiclecollections=mongo_db.puc_info
            existing_vehicle = vehiclecollections.find_one({"reg_no": rc_number})

            if existing_vehicle:
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
                    "vehicle_pucc_details": vehicle_pucc_details
                }

                result_rto_info.append(formatted_data)
                continue

            print("extracting rto info")
            rto_response = perform_puc_validation(rc_number)
            if "error" in rto_response:
                error_message=rto_response["error"]
                return Response(
                    response=json.dumps({'status': "failed", "message": f"Validation Error: {error_message}"}),
                    status=400,
                    mimetype='application/json'
                )
            message = ""
            vehicle_pucc_details = rto_response["result"]["vehicle_pucc_details"]
            if vehicle_pucc_details is not None:
                message = "PUC is Valid!!"
            else:
                message = "PUC is InValid!!"
            reg_no = rto_response["result"]["reg_no"]
            owner_name = rto_response["result"]["owner_name"]
            model = rto_response["result"]["model"]
            state = rto_response["result"]["state"]

            formatted_data = {
                "message": message,
                "reg_no": reg_no,
                "owner_name": owner_name,
                "model": model,
                "state": state,
                "vehicle_pucc_details": vehicle_pucc_details
            }

            print("Saving in db!!")
            vehicle_details = VehicleDetails(
                reg_no=formatted_data["reg_no"],
                owner_name=formatted_data["owner_name"],
                model=formatted_data["model"],
                state=formatted_data["state"],
                vehicle_pucc_details=formatted_data["vehicle_pucc_details"]
            )

            vehicle_details.save_to_db()

            print("Saved in db")
            result_rto_info.append(formatted_data)

        return Response(json.dumps({
            'response':result_rto_info,
            'status': "success",
            'message': "Image processing done successfully",
        }), status=200, mimetype='application/json')
    
    except Exception as e:
        return Response(
            response=json.dumps({'status': "failed",
                                 "message": "Error Occurred",
                                 "error": str(e)}),
            status=500,
            mimetype='application/json'
        )