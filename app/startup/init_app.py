# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from flask_mail import Mail
from flask_migrate import Migrate, MigrateCommand
from flask_user import UserManager, SQLAlchemyAdapter
from flask_wtf.csrf import CsrfProtect
from app import app, db, manager


@app.before_first_request
def initialize_app_on_first_request():
    from .create_users import create_users
    create_users()


def create_app(extra_config_settings={}):
    """
    Initialize Flask applicaton
    """

    # Initialize app config settings
    app.config.from_object('app.startup.settings')          # Read config from 'app/startup/settings.py' file
    app.config.update(extra_config_settings)                # Overwrite with 'extra_config_settings' parameter
    if app.testing:
        app.config['WTF_CSRF_ENABLED'] = False              # Disable CSRF checks while testing

    # Setup Flask-Migrate
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)

    # Setup Flask-Mail
    mail = Mail(app)

    # Setup WTForms CsrfProtect
    CsrfProtect(app)

    # Define bootstrap_is_hidden_field for flask-bootstrap's bootstrap_wtf.html
    from wtforms.fields import HiddenField
    def is_hidden_field_filter(field):
        return isinstance(field, HiddenField)
    app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter

    # Setup an error-logger to send emails to app.config.ADMINS
    init_email_error_handler(app)

    # Setup Flask-User to handle user account related forms
    from app.models import User, MyRegisterForm
    from app.views.user_views import user_profile_page
    db_adapter = SQLAlchemyAdapter(db, User)        # Setup the SQLAlchemy DB Adapter
    user_manager = UserManager(db_adapter, app,     # Init Flask-User and bind to app
            register_form=MyRegisterForm,           #   using a custom register form with UserProfile fields
            user_profile_view_function = user_profile_page,
            )

    # Load all models.py files to register db.Models with SQLAlchemy
    from app import models

    # Load all views.py files to register @app.routes() with Flask
    from app.views import page_views, user_views

    return app


def init_email_error_handler(app):
    """
    Initialize a logger to send emails on error-level messages.
    Unhandled exceptions will now send an email message to app.config.ADMINS.
    """
    if app.debug: return                        # Do not send error emails while developing

    # Retrieve email settings from app.config
    host      = app.config['MAIL_SERVER']
    port      = app.config['MAIL_PORT']
    from_addr = app.config['MAIL_DEFAULT_SENDER']
    username  = app.config['MAIL_USERNAME']
    password  = app.config['MAIL_PASSWORD']
    secure = () if app.config.get('MAIL_USE_TLS') else None

    # Retrieve app settings from app.config
    to_addr_list = app.config['ADMINS']
    subject = app.config.get('APP_SYSTEM_ERROR_SUBJECT_LINE', 'System Error')

    # Setup an SMTP mail handler for error-level messages
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler(
        mailhost=(host, port),                  # Mail host and port
        fromaddr=from_addr,                     # From address
        toaddrs=to_addr_list,                   # To address
        subject=subject,                        # Subject line
        credentials=(username, password),       # Credentials
        secure=secure,
    )
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    # Log errors using: app.logger.error('Some error message')




