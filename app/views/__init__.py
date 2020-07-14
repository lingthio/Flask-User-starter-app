# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.
from flask import Blueprint

from app.views.main_views import main_blueprint
from app.views.admin_views import admin_blueprint

def register_blueprints(app, url_prefix=""):
    app.register_blueprint(main_blueprint, url_prefix=url_prefix)
    app.register_blueprint(admin_blueprint, url_prefix=url_prefix)

