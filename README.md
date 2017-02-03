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

Settings common to all environments are found in `app/settings.py`. DO NOT store any security
settings in this file as it's going to be checked into the code repository.

Environment specific settings are stored in `app/local_settings.py` that is NOT stored in the code repository.
The example `app/local_settings_example.py` can be used as a starting point::

    cd ~/dev/my_app
    cp app/local_settings_example.py app/local_settings.py

Configure `app/local_settings.py`.

## Configuring the SMTP server

Edit ~/dev/my_app/app/env_settings.py.

Make sure to configure all the MAIL_... settings correctly.

Note: For smtp.gmail.com to work, you MUST set "Allow less secure apps" to ON in Google Accounts.
Change it in https://myaccount.google.com/security#connectedapps (near the bottom).

## Initializing the Database

    # Create DB tables and populate the roles and users tables
    python manage.py init_db


## Running the app

    # Start the Flask development web server
    python manage.py runserver

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

