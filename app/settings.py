# Settings common to all environments (development|staging|production)
# Place environment specific settings in env_settings.py
# An example file (env_settings_example.py) can be used as a starting point

import os

# Application settings
APP_NAME = "ISSM"
APP_SYSTEM_ERROR_SUBJECT_LINE = APP_NAME + " system error"

# Flask settings
CSRF_ENABLED = True
WTF_CSRF_ENABLED = False # see __init__.py => check_csrf()
WTF_CSRF_CHECK_DEFAULT = False

# Flask-SQLAlchemy settings
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-User settings
USER_APP_NAME = APP_NAME
USER_ENABLE_CHANGE_PASSWORD = True  # Allow users to change their password
USER_ENABLE_CHANGE_USERNAME = False  # Allow users to change their username
USER_ENABLE_CONFIRM_EMAIL = False  # Force users to confirm their email
USER_ENABLE_FORGOT_PASSWORD = False  # Allow users to reset their passwords
USER_ENABLE_EMAIL = True  # Register with Email
USER_ENABLE_REGISTRATION = False  # Allow new users to register
USER_REQUIRE_RETYPE_PASSWORD = True  # Prompt for `retype password` in:
USER_ENABLE_USERNAME = False  # Register and Login with username
USER_AFTER_LOGIN_ENDPOINT = 'view.main.get_project_overview_page'
USER_AFTER_LOGOUT_ENDPOINT = 'view.main.get_project_overview_page'

from pathlib import Path

VERSION = Path('Version').read_text()
