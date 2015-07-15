# Flask-User starter app

This code base serves as a great starting point to write your next Flask application
(With or without Flask-User)

## Developer benefits
* Tested on Python 2.7, 3.3, and 3.4
* Few dependencies (Flask-Migrate, Flask-SQLAlchemy, Flask-User, Flask-WTF)
* Carefully chosen names for files, classes and methods
* Well organized directories with lots of comments
  * app/models
  * app/startup
  * app/views
* Customizable base templates that defaults to Bootstrap3
* Includes user management pages using Flask-User
  * Register, Confirm email, Login, Logout
  * Change username/email/password, Forgot password
* One generic settings.py file
  * with sensible defaults for development environments
  * with secure overwrite for production environments through OS environment settings
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
    python runserver.py

Point your web browser to http://localhost:5000/

You can make use of the following users:
- username `member` with password `Password1`.
- username `admin` with password `Password1`.


## Testing the app (with coverage)

    # Run all the automated tests in the tests/ directory
    ./runtests.sh

The output will show a test coverage report.


## Acknowledgements
With thanks to the following Flask extensions:

* [Alembic](alembic.readthedocs.org)
* [Flask-Migrate](flask-migrate.readthedocs.org)
* [Flask-User](pythonhosted.org/Flask-User/)

[Flask-User-starter-app](https://github.com/lingthio/Flask-User-starter-app) was used as a starting point for this code repository.

    # Please consider leaving the line above in your project's README file. Thank you.

