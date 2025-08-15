import os
import sys
import logging
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics
import routes

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Validate and set SECRET_KEY with minimum length requirement
session_secret = os.environ.get(
    'SESSION_SECRET', 'dev-secret-key-change-in-production'
)
if session_secret == 'dev-secret-key-change-in-production':
    logging.warning(
        "Using default development SECRET_KEY. Set SESSION_SECRET "
        "environment variable in production!"
    )
elif len(session_secret) < 32:
    logging.error(
        "SESSION_SECRET must be at least 32 characters long for security"
    )
    sys.exit(1)
else:
    logging.warning(
        "Session secret loaded successfully from environment variable "
        "SESSION_SECRET"
    )

app.config['SECRET_KEY'] = session_secret

# Configure rate limiting
# Default limits: 200 requests per day, 50 per hour
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)

# Register routes after app initialization to avoid circular imports
routes.register_routes(app, limiter)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
