import requests
import os
import subprocess
from io import BytesIO
from PIL import Image
from flask import request, Response, json, Blueprint
from werkzeug.utils import secure_filename

image_processing = Blueprint("image_processing", __name__)

@image_processing.route('/process_image',methods=["POST"])
def process_image():
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
            'error': response.json()
        }), status=response.status_code, mimetype='application/json')
    
    print("image processed by model")

    # Remove the temporary file
    try:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    except Exception as e:
        print("Error deleting temporary file:", e)

    print("performing ocr")

    image_dir = os.path.dirname(__file__)
    while not os.path.isfile(os.path.join(image_dir, 'requirements.txt')):
        image_dir = os.path.dirname(image_dir)
    image_dir+='/results'

    headers = {
        'X-RapidAPI-Key': '0cbdcbfe4cmsh1e8541eecba47ebp1f85d7jsn650f234d3ec9',
        'X-RapidAPI-Host': 'ocr43.p.rapidapi.com'
    }

    image_processed_data=[]

    for filename in os.listdir(image_dir):
        file_path = os.path.join(image_dir, filename)

        # Open the image file and convert it to RGB
        image = Image.open(file_path).convert("RGB")
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        form_data = {
            'image': ('image.jpg', img_byte_arr)
        }

        response = requests.post('https://ocr43.p.rapidapi.com/v1/results', headers=headers, files=form_data)
        ocr_response=response.json()
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
            print("Error deleting temporary file:", e)

    return Response(json.dumps({
        'response':image_processed_data,
        'status': "success",
        'message': "Image processing done successfully",
    }), status=200, mimetype='application/json')