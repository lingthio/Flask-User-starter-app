# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.
from flask import Blueprint

from .main_views import main_blueprint
from .admin_views import admin_blueprint
import app.views.data_api.case_data
import app.views.data_api.case_meta_data
import app.views.data_api.projects


def register_blueprints(app):
    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint)

