from flask import request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
import logging

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def init_middleware(app):
    # Initialize rate limiter with the app
    limiter.init_app(app)

    @app.before_request
    def before_request():
        # Store request start time
        g.start_time = time.time()

        # Log incoming request
        logging.info(f"Request started: {request.method} {request.path}")
        if request.is_json:
            logging.debug(f"Request JSON: {request.get_json()}")

    @app.after_request
    def after_request(response):
        # Calculate request duration
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            logging.info(f"Request completed in {duration:.2f}s: {request.method} {request.path} - {response.status_code}")

        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        return response

# Decorator for rate limiting
def apply_rate_limits(app):
    # Apply rate limits after routes are registered
    app.view_functions['melody_matching'] = limiter.limit("3 per minute")(app.view_functions['melody_matching'])
    app.view_functions['lyrics_matching'] = limiter.limit("10 per minute")(app.view_functions['lyrics_matching'])