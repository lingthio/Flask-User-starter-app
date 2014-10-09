# Application settings are stored in two files:
# - local_settings.py contain settings that are environment-specific or security related
#   This file is NOT checked into the code repository.
#   See also local_settings_example.py (which IS part of the code repository).
# - settings.py contain settings that are the same across different environments
#   This file IS checked into the code repository.

import os

# Get application base dir.
_basedir = os.path.abspath(os.path.dirname(__file__))

# Flask settings
CSRF_ENABLED = True

# Application settings
APP_NAME = "AppName"
APP_SYSTEM_ERROR_SUBJECT_LINE = APP_NAME + " system error"