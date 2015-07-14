# Flask-User starter app

This code base serves as a great starting point to write your next Flask application  
(With or without Flask-User)

* Well organized directories with lots of comments
  * app/models
  * app/startup
  * app/views
* Carefully chosen names for files, classes and methods
* Few dependencies (Flask-SQLAlchemy, Flask-User, Flask-WTF)
* Includes user management pages using Flask-User
  * Register, Confirm email, Login, Logout
  * Change username/email/password, Forgot password
* Includes `py.test` test framework
* Includes `alembic` database migration framework
* Customizable base templates that defaults to Bootstrap3
* One generic settings.py file
  * with sensible defaults for development environments
  * with secure overwrite for production environments through OS environment settings 
* SMTPHandler for error-level log messages -- sends emails on unhandled exceptions
* Tested on Python 2.7, 3.3, 3.4


## Cloning the code base
We assume that you have `git` and `virtualenvwrapper` installed.

    # Clone the code repository into ~/dev/my_app
    mkdir -p ~/dev
    cd ~/dev
    git clone https://github.com/lingthio/Flask-User-starter-app.git my_app
    cd ~/dev/my_app

    # Create the 'my_app' virtual environment and install required python packages
    mkvirtualenv -p PATH/TO/PYTHON my_app
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

    # Configure the email addresses to receive system error email notifications
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


## Automated tests and code coverage using py.test

    # Run all the automated tests in the tests/ directory
    workon my_app
    cd ~/dev/my_app
    ./runtests.sh


## Acknowledgements
If you feel generous, please consider leaving this 'Acknowledgement' section in your README file. Thank you.

This project used [Flask-User-starter-app](https://github.com/lingthio/Flask-User-starter-app) as a starting point.

