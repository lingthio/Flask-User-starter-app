import os

def get(var):
    return os.environ.get(var)

def getbool(var):
    val = int(get(var))
    assert val in [0, 1], f'{var} must be a boolen (0, 1)'
    return bool(val)

def getlist(var):
    return var.split(',')

# *****************************
# Environment specific settings
# *****************************

# DO NOT use "DEBUG = True" in production environments
DEBUG = getbool('DEBUG')

# DO NOT use Unsecure Secrets in production environments
SECRET_KEY = get('SECRET_KEY')

# path to data directory for images and segmentations
DATA_PATH = get('DATA_PATH')

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = get('DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids a SQLAlchemy Warning

# Flask-Mail settings
MAIL_SERVER = get('MAIL_SERVER')
MAIL_PORT = get('MAIL_PORT')
MAIL_USE_SSL = getbool('MAIL_USE_SSL')
MAIL_USE_TLS = getbool('MAIL_USE_TLS')
MAIL_USERNAME = get('MAIL_USERNAME')
MAIL_PASSWORD = get('MAIL_PASSWORD')

# Sendgrid settings
SENDGRID_API_KEY = get('SENDGRID_API_KEY')

# Flask-User settings
USER_APP_NAME = get('APP_NAME')
USER_EMAIL_SENDER_NAME = get('EMAIL_SENDER_NAME')
USER_EMAIL_SENDER_EMAIL = get('EMAIL_SENDER_EMAIL')
MAIL_DEFAULT_SENDER = get('EMAIL_SENDER_NAME')


