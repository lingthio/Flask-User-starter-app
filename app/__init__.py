# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

from datetime import datetime
import os

from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter
from flask_wtf.csrf import CSRFProtect

# Instantiate Flask extensions
db = SQLAlchemy()
csrf_protect = CSRFProtect()
mail = Mail()
migrate = Migrate()


def create_app(extra_config_settings={}):
    """Create a Flask applicaction.
    """
    # Instantiate Flask
    app = Flask(__name__)

    # Load App Config settings
    # Load common settings from 'app/settings.py' file
    app.config.from_object('app.settings')
    # Load local settings from 'app/local_settings.py'
    app.config.from_object('app.local_settings')
    # Load extra config settings from 'extra_config_settings' param
    app.config.update(extra_config_settings)

    # Setup Flask-Extensions -- do this _after_ app config has been loaded

    # Setup Flask-SQLAlchemy
    db.init_app(app)

    # Setup Flask-Migrate
    migrate.init_app(app, db)

    # Setup Flask-Mail
    mail.init_app(app)

    # Setup WTForms CSRFProtect
    csrf_protect.init_app(app)

    # Register blueprints
    from app.views.misc_views import main_blueprint
    app.register_blueprint(main_blueprint)

    # Define bootstrap_is_hidden_field for flask-bootstrap's bootstrap_wtf.html
    from wtforms.fields import HiddenField

    def is_hidden_field_filter(field):
        return isinstance(field, HiddenField)

    app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter

    # Setup an error-logger to send emails to app.config.ADMINS
    init_email_error_handler(app)

    # Setup Flask-User to handle user account related forms
    from .models.user_models import User, MyRegisterForm
    from .views.misc_views import user_profile_page

    db_adapter = SQLAlchemyAdapter(db, User)  # Setup the SQLAlchemy DB Adapter
    user_manager = UserManager(db_adapter, app,  # Init Flask-User and bind to app
                               register_form=MyRegisterForm,  # using a custom register form with UserProfile fields
                               user_profile_view_function=user_profile_page,
    )

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
    to_addr_list = app.config['ADMINS']
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




