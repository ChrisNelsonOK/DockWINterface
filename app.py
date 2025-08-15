import os
import logging
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.INFO)  # Production logging level

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Import routes after app creation to avoid circular imports
from routes import *
