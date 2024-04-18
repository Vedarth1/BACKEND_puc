import os
import json
from io import BytesIO
import requests
from PIL import Image

image_dir = "D:/WTF/backend_bb/Project 6th sem/Detection-model/results"

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

    # Make POST request to OCR API endpoint
    headers = {
        'X-RapidAPI-Key': '139c90d5bdmsh887cd3b63935516p1969a0jsn785beb400347',
        'X-RapidAPI-Host': 'ocr43.p.rapidapi.com'
    }
    response = requests.post('https://ocr43.p.rapidapi.com/v1/results', headers=headers, files=form_data)

    ocr_response=response.json()
    text=ocr_response['results'][0]['entities'][0]['objects'][0]['entities'][0]['text']
    if response.status_code == 200:
        print(text)
    else:
        print("Error performing OCR")