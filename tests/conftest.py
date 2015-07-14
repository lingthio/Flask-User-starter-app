# This file contains pytest 'fixtures'.
# If a test functions specifies the name of a fixture function as a parameter,
# the fixture function is called and its result is passed to the test function.
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import pytest
from app import create_app, db as the_db

# Initialize the Flask-App with test-specific settings
the_app = create_app(dict(
    TESTING=True,               # Propagate exceptions
    LOGIN_DISABLED=False,       # Enable @register_required
    MAIL_SUPPRESS_SEND=True,    # Disable Flask-Mail send
    SERVER_NAME='localhost',    # Enable url_for() without request context
    SQLALCHEMY_DATABASE_URI='sqlite:///:memory:', # In-memory SQLite DB
    WTF_CSRF_ENABLED=False,     # Disable CSRF form validation
    ))

# Setup an application context (since the tests run outside of the webserver context)
the_app.app_context().push()

@pytest.fixture(scope='session')
def app():

    return the_app

@pytest.fixture(scope='session')
def db():
    """
    Initializes and returns a SQLAlchemy DB object
    """
    return the_db
