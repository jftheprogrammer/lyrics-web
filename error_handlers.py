from flask import jsonify
from werkzeug.exceptions import HTTPException
import logging

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the error
        logging.exception("An unexpected error occurred")
        
        # Handle HTTP exceptions
        if isinstance(e, HTTPException):
            response = {
                "error": e.name,
                "message": e.description,
                "status_code": e.code
            }
            return jsonify(response), e.code
            
        # Handle other exceptions
        response = {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "status_code": 500
        }
        return jsonify(response), 500

    @app.errorhandler(429)
    def handle_ratelimit(e):
        return jsonify({
            "error": "Too Many Requests",
            "message": "Please wait before trying again.",
            "status_code": 429
        }), 429

    @app.errorhandler(413)
    def handle_large_file(e):
        return jsonify({
            "error": "File Too Large",
            "message": "The uploaded file exceeds the maximum allowed size.",
            "status_code": 413
        }), 413
