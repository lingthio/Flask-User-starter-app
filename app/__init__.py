# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# This is the WSGI compliant web application object
app = Flask(__name__)

# Setup Flask-SQLAlchemy
db = SQLAlchemy(app)

from app.startup.init_app import create_app, create_users