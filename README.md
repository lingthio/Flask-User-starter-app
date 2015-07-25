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

Instead of editing app/config/settings.py and checking in sensitive information into
the code repository, these settings can be overruled by the following OS environment settings:

    # Configure your Database
    export DATABASE_URL='sqlite:///app.sqlite'

    # Configure your SMTP provider
    export MAIL_USERNAME='email@example.com'
    export MAIL_PASSWORD='password'
    export MAIL_DEFAULT_SENDER='"MyApp" <noreply@example.com>'
    export MAIL_SERVER='smtp.gmail.com'
    export MAIL_PORT='465'
    export MAIL_USE_SSL='1'

    # Configure the admin that is going to emails regarding system errors
    export ADMIN1='"Admin One" <user_one@example.com>'
    export ADMIN2='"Admin Two" <user_two@example.com>'

For convenience, you can set these settings in your ``~/.bashrc`` or ``~/.bash_profile`` shell configuration file.


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

