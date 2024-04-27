from flask import request, Response, json, Blueprint
from src.services.validation_service import perform_puc_validation

puc_validation = Blueprint("puc_validation", __name__)

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
        
        result = perform_puc_validation(data["rc_number"])
        return Response(
            response=json.dumps(result),
            status=200 if result['status'] == 'success' else 400,
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
