# Flask-User starter app

This code base serves as a great starting point to write your next Flask application  
(With or without Flask-User)

## Developer benefits
* Tested on Python 2.7, 3.3, and 3.4
* Well organized directories with lots of comments
  * app/models
  * app/startup
  * app/views
* HTML5 BoilerPlate / jQuery / Bootstrap layout template
* Few dependencies (Flask-SQLAlchemy, Flask-WTF, Flask-User, Flask-Migrate)
* Includes Flask-User user management
  * Register, Confirm email, Login, Logout
  * Change username/email/password, Forgot password
* SMTPHandler for error-level log messages -- sends emails on unhandled exceptions
* Includes `py.test` test framework
* Includes `alembic` database migration framework


## Cloning the code base
We assume that you have `git` and `virtualenvwrapper` installed.

    # Clone the code repository into ~/dev/my_app
    mkdir -p ~/dev
    cd ~/dev
    git clone https://github.com/lingthio/Flask-User-starter-app.git my_app

    # Create the 'my_app' virtual environment
    mkvirtualenv -p PATH/TO/PYTHON my_app

    # Install required Python packages
    cd ~/dev/my_app
    workon my_app
    pip install -r requirements.txt
    
    
## Configuring the app

Before we can use this application, we will have to configure the database URL and SMTP account
that will be used to access the database and to send emails.

Settings common to all environments are found in app/startup/common_settings.py

The example environment-specific settings are found in app/env_settings_example.py

Note: DO NOT edit app/config/settings.py because checking this into the core repository
will expose security sensitive information.

Copy the `app/env_settings_example.py` to an `env_settings.py` that resides **outside** the code directory
and point the OS environment variable `ENV_SETTINGS_FILE` to this file.

    # Copy env_settings.py and place it outside of the code directory
    cd /path/to/project
    cp app/env_settings_example.py ../env_settings.py
    
    # Point the OS environment variable `ENV_SETTINGS_FILE` to this file
    export ENV_SETTINGS_FILE=/path/to/env_settings.py

For convenience, you can set ENV_SETTINGS_FILE in your ``~/.bashrc`` or ``~/.bash_profile`` shell configuration file.

Now edit the /path/to/env_settings.py file.


## Initializing the Database
    # Create DB tables and populate the roles and users tables
    python manage.py init_db


## Running the app

    # Start the Flask development web server
    ./runserver.sh    # will run "python manage.py runserver"

Point your web browser to http://localhost:5000/

You can make use of the following users:
- email `user@example.com` with password `Password1`.
- email `admin@example.com` with password `Password1`.


## Testing the app

    # Run all the automated tests in the tests/ directory
    ./runtests.sh         # will run "py.test -s tests/"


## Generating a test coverage report

    # Run tests and show a test coverage report
    ./runcoverage.sh      # will run py.test with coverage options

## Database migrations

    # Show all DB migration commands
    python manage.py db

See [the Alembic docs](alembic.readthedocs.org) for more information.


## Trouble shooting
If you make changes in the Models and run into DB schema issues, delete the sqlite DB file `app/app.sqlite`.


## Acknowledgements
With thanks to the following Flask extensions:

* [Alembic](alembic.readthedocs.org)
* [Flask-Migrate](flask-migrate.readthedocs.org)
* [Flask-User](pythonhosted.org/Flask-User/)

[Flask-User-starter-app](https://github.com/lingthio/Flask-User-starter-app) was used as a starting point for this code repository.

    # Please consider leaving the line above in your project's README file. Thank you.

