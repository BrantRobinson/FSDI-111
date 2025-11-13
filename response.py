from flask import jsonify

#GET, PUT/PATCH, DELETE
def success_response(message:str, data=None):
    """
        Generic Success Response for GET, PUT/PATCH and DELETE.
    """
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), 200

def not_found(entity:str="Resource"):
    """
        Generate a standard 404 not found JSON response
    """
    return jsonify({
        "success": False,
        "message": f"{entity} not found"
    }), 404