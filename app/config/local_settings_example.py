# Application settings are stored in two files:
# - local_settings.py contain settings that are environment-specific or security related
#   This file is NOT checked into the code repository.
#   See also local_settings_example.py (which IS part of the code repository).
# - settings.py contain settings that are the same across different environments
#   This file IS checked into the code repository.

# Flask settings
SECRET_KEY = '\xb9\x8d\xb5\xc2\xc4Q\xe7\x8ej\xe0\x05\xf3\xa3kp\x99l\xe7\xf2i\x00\xb1-\xcd'  # Generated with: import os; os.urandom(24)

# Flask-Mail settings for smtp.webfaction.com
MAIL_USERNAME = 'YOURNAME@gmail.com'
MAIL_PASSWORD = 'YOURPASSWORD'
MAIL_DEFAULT_SENDER = 'NOREPLY <noreply@gmail.com>'

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_SSL = False
MAIL_USE_TLS = True

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.sqlite'       # SQLite DB

# Admins to receive System Error emails
ADMINS = [
    '"YOUR NAME" <YOURNAME@gmail.com>',
    ]
