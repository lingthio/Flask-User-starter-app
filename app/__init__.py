# The __init__.py files make Python's import statement work inside subdirectories.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# This is the WSGI compliant web application object
app = Flask(__name__)

# Setup Flask-SQLAlchemy
db = SQLAlchemy(app)

from app.startup.init_app import create_app, create_users