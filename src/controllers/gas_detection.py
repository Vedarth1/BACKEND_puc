import os
from flask import request, Response, json, Blueprint

gas_detection = Blueprint("gas_detection", __name__)

@gas_detection.route('/gas_detection', methods=["POST"])
def process_gas_data():
    try:
        # Ensure the request is JSON
        if not request.is_json:
            return Response(
                response=json.dumps({'error': 'Request must be JSON'}),
                status=400,
                mimetype='application/json'
            )
        
        # Parse the JSON data
        data = request.get_json()
        rs_ro_ratio = data.get('rs_ro_ratio')
        ppm = data.get('ppm')

        # Validate the input data
        if rs_ro_ratio is None or ppm is None:
            return Response(
                response=json.dumps({'error': 'Missing rs_ro_ratio or ppm in request data'}),
                status=400,
                mimetype='application/json'
            )

        print(f"Received data - RS/R0 Ratio: {rs_ro_ratio}, PPM: {ppm}")

        # Here you can process the data, save to the database, etc.
        # For example:
        # gas_data = GasData(rs_ro_ratio=rs_ro_ratio, ppm=ppm)
        # gas_data.save_to_db()

        print("Data processed successfully")

        return Response(
            response=json.dumps({
                'status': "success",
                'message': "Gas data processed successfully",
                'received_data': {
                    'rs_ro_ratio': rs_ro_ratio,
                    'ppm': ppm
                }
            }),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        return Response(
            response=json.dumps({
                'status': "failed",
                'message': "Error occurred",
                'error': str(e)
            }),
            status=500,
            mimetype='application/json'
        )
