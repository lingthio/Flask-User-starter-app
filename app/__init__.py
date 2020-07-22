# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

from datetime import datetime
import os
import logging

from flask_script import Manager

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate, MigrateCommand
from flask_wtf.csrf import CSRFProtect
from flask_scss import Scss

from flask_user import UserManager, current_user
from flask_admin import Admin

from werkzeug.local import LocalProxy

logging.getLogger().setLevel(logging.INFO)

app = None
current_project = None
user_manager = None

# Instantiate Flask extensions
csrf_protect = CSRFProtect()
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
flask_admin = Admin(url='/admin/flask_admin')

# Initialize Flask Application
def create_app(extra_config_settings={}):
    """Create a Flask application.
    """

    global app, current_project, user_manager

    # Instantiate Flask
    app = Flask(__name__)

    app.logger.info("Created Flask Application")

    # Load common settings
    app.config.from_object('app.settings')
    # Load environment specific settings
    app.config.from_object('app.local_settings')
    # Load extra settings from extra_config_settings param
    app.config.update(extra_config_settings)

    # import utils here, because they need the initialized app variable
    from app import utils

    current_project = LocalProxy(lambda: utils.get_current_project())

    Scss(app, static_dir='app/static', asset_dir='app/assets')

    # Setup Flask-SQLAlchemy
    db.init_app(app)

    # Setup Flask-Migrate
    migrate.init_app(app, db)

    # Setup Flask-Mail
    mail.init_app(app)

    # Setup Flask-Admin
    flask_admin.init_app(app)

    # Setup WTForms CSRFProtect
    csrf_protect.init_app(app)

    # Register REST Api
    from app.services import register_blueprints as register_api
    register_api(app, url_prefix="/api", exempt_from_csrf = True, csrf_protect = csrf_protect)
    csrf_protect
    
    # Register views
    from app.views import register_blueprints as register_view
    register_view(app, url_prefix="")

    # app.logger.info(app.url_map)

    # Define bootstrap_is_hidden_field for flask-bootstrap's bootstrap_wtf.html
    from wtforms.fields import HiddenField

    def is_hidden_field_filter(field):
        return isinstance(field, HiddenField)

    app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter

    # Setup an error-logger to send emails to app.config.ADMINS
    init_email_error_handler(app)

    # Setup Flask-User to handle user account related forms
    from .models.user_models import User
    #from .views.main_views import user_profile_page

    # Setup Flask-User
    user_manager = UserManager(app, db, User)

    # registers all jinja template extensions
    from app import template_extensions

    # enable CSRF-Protection for all view urls and only exclude /user and /api

    """
    remove CSRF check from all requests with settings.py
    via WTF_CSRF_CHECK_DEFAULT to False
    
    and only add it to the view requests:
    """
    @app.before_request
    def check_csrf():
        if not request.path.startswith('/user') and not request.path.startswith('/api'):
            app.logger.debug(f"CSRF protecting path {request.path}")
            csrf_protect.protect()


    # for key in app.config:
    #     app.logger.info(f"{key} {app.config[key]}")

    if not app.debug:
        users = []

        with app.app_context():
            # init db
            db.create_all()

            from app.models.user_models import User
            users = db.session.query(User).all()

            # check if there are already technical users existing (if so, then this is not the first boot)
            no_technical_admin = False if any(user if any(role.name == 'admin' for role in user.roles) else None for user in users) else True

            app.logger.info(f"No technical admin present? {no_technical_admin}")

            # create default admin if no user exist
            if no_technical_admin:
                from app.commands.init_db import create_roles
                create_roles()

                # create the default flask admin
                from app.models.user_models import Role
                from app.controllers import user_controller
                all_roles = Role.query.all()
                # app.logger.info(f"Creating admin with attributes: 'Admin', 'Admin', {app.config['ADMIN']}, {app.config['ADMIN_PW']}, {all_roles}")
                default_admin_user = user_controller.create_user('Admin', 'Admin', app.config['ADMIN'], app.config['ADMIN_PW'], all_roles)

    return app


def init_email_error_handler(app):
    """
    Initialize a logger to send emails on error-level messages.
    Unhandled exceptions will now send an email message to app.config.ADMINS.
    """
    if app.debug: return  # Do not send error emails while developing

    # Retrieve email settings from app.config
    host = app.config['MAIL_SERVER']
    port = app.config['MAIL_PORT']
    from_addr = app.config['MAIL_DEFAULT_SENDER']
    username = app.config['MAIL_USERNAME']
    password = app.config['MAIL_PASSWORD']
    secure = () if app.config.get('MAIL_USE_TLS') else None

    # Retrieve app settings from app.config
    to_addr_list = app.config['ADMIN']
    subject = app.config.get('APP_SYSTEM_ERROR_SUBJECT_LINE', 'System Error')

    # Setup an SMTP mail handler for error-level messages
    import logging
    from logging.handlers import SMTPHandler

    mail_handler = SMTPHandler(
        mailhost=(host, port),  # Mail host and port
        fromaddr=from_addr,  # From address
        toaddrs=to_addr_list,  # To address
        subject=subject,  # Subject line
        credentials=(username, password),  # Credentials
        secure=secure,
    )
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    # Log errors using: app.logger.error('Some error message')





