# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)           # The WSGI compliant web application object
manager = Manager(app)          # Setup Flask-Script
db = SQLAlchemy()               # Setup Flask-SQLAlchemy

from app.create_app import create_app, create_users
from .manage_commands import init_db      # Explicit import to work with Python3
