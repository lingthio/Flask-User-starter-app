# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

from flask import Blueprint

from .data_pool_service import data_pool_service
from .project_service import project_service
from .user_service import user_service

all_services = [data_pool_service, project_service, user_service]


def register_blueprints(app, url_prefix = "/api", exempt_from_csrf = False, csrf_protect = None):

    for service in all_services:
        app.register_blueprint(service, url_prefix=url_prefix + service.url_prefix)
        if exempt_from_csrf:
            csrf_protect.exempt(service)

