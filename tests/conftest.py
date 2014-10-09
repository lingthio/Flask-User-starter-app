# This file contains pytest 'fixtures'.
# If a test functions specifies the name of a fixture function as a parameter,
# the fixture function is called and its result is passed to the test function.
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import pytest
from app.app_and_db import app as flask_app, db as sqlalchemy_db
from app.startup.init_app import init_app

@pytest.fixture(scope='module')
def app():
    """
    Initializes and returns a Flask application object
    """
    # Initialize the Flask-App with test-specific settings
    test_config_settings = dict(
        TESTING=True,               # Propagate exceptions
        LOGIN_DISABLED=False,       # Enable @register_required
        MAIL_SUPPRESS_SEND=True,    # Disable Flask-Mail send
        SERVER_NAME='localhost',    # Enable url_for() without request context
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:', # In-memory SQLite DB
        WTF_CSRF_ENABLED=False,     # Disable CSRF form validation
        )
    init_app(flask_app, sqlalchemy_db, test_config_settings)

    # Setup an application context (since the tests run outside of the webserver context)
    flask_app.app_context().push()

    return flask_app

@pytest.fixture(scope='module')
def db():
    """
    Initializes and returns a SQLAlchemy DB object
    """
    return sqlalchemy_db
