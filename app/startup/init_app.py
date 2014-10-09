# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import logging
from logging.handlers import SMTPHandler
from flask_mail import Mail
from flask_user import UserManager, SQLAlchemyAdapter

def init_app(app, db, extra_config_settings={}):
    """
    Initialize Flask applicaton
    """

    # Initialize app config settings
    # - settings.py is checked into Git.
    # - local_settings.py is different for each deployment
    # - extra_config_settings{} is specified by the automated test suite
    app.config.from_object('app.config.settings')           # Read config from 'app/settings.py' file
    app.config.from_object('app.config.local_settings')     # Overwrite with 'app/local_settings.py' file
    app.config.update(extra_config_settings)                       # Overwrite with 'extra_config_settings' parameter
    if app.testing:
        app.config['WTF_CSRF_ENABLED'] = False              # Disable CSRF checks while testing

    # Setup Flask-Mail
    mail = Mail(app)

    # Setup an error-logger to send emails to app.config.ADMINS
    init_error_logger_with_email_handler(app)

    # Setup Flask-User to handle user account related forms
    from app.users.models import User, UserProfile
    from app.users.forms import MyRegisterForm
    db_adapter = SQLAlchemyAdapter(db, User,        # Select database adapter
            UserProfileClass=UserProfile)           #   with a custom UserProfile model
    user_manager = UserManager(db_adapter, app,     # Init Flask-User and bind to app
            register_form=MyRegisterForm)           #   using a custom register form with UserProfile fields

    # Load all models.py files to register db.Models with SQLAlchemy
    from app.users import models

    # Load all views.py files to register @app.routes() with Flask
    from app.pages import views
    from app.users import views

    # Automatically create all DB tables in app/app.sqlite file
    db.create_all()

    return app


def init_error_logger_with_email_handler(app):
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
