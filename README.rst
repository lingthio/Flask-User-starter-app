Flask-User starter app
========

This code base serves as a great starting point to write your next Flask application.


**Development Feature set**

* Modular and well-document directory structure with _readme.txt files.
* Well-named source code files with lots of helpful comments.
* Separate ``settings.py`` for general settings and ``local_settings.py`` for environment-specific settings.
* Bootstrap3 base template that can easily be changed.
* Complete with a skeleton for an automated test suite.

It's a great starting point for new Flask applications -- whether you plan to use Flask-User or not.


**Application Feature set**

* Home page
* User Profile page
* User account management (Register, Confirm, Forgot password,
  Login, Change username, Change password, Logout) using Flask-User
* SMTPHandler for error-level log messages -- sends emails on unhandled exceptions


**Dependencies**

* Flask
* Flask-SQLAlchemy
* Flask-User v0.6 and up (v0.5 does not support UserAuthClass)


Installation
--------

**Install git**

See http://git-scm.com/book/en/Getting-Started-Installing-Git

**Clone this github repository**

Open a command line shell and type:

::

  mkdir -p ~/dev
  cd ~/dev
  git clone https://github.com/lingthio/Flask-User-starter-app.git my_app
  cd ~/dev/my_app

**Install virtualenvwrapper**

Install it with::

  sudo pip install virtualenvwrapper

Configure it with::

  export WORKON_HOME=$HOME/.virtualenvs
  export PROJECT_HOME=$HOME/dev
  source /usr/local/bin/virtualenvwrapper.sh

You may want to place the above in your .bashrc or .profile or .bash_profile file

See http://virtualenvwrapper.readthedocs.org/en/latest/install.html

**Create a new virtualenv**

Find a Python 2.7 executable using ``python --version`` and ``which python``.

Run this command once:

::

  mkvirtualenv -p /full/path/to/python2.7 my_app
  workon my_app

where the result of ``which python`` can be used instead of ``/full/path/to/python2.7``,
and where ``my_app`` is the name of the new virtualenv.

**Install Fabric**

Fabric is a build and deployment tool that uses the Python language for its scripts.
Though the product name is 'Fabric', the command line tool is 'fab'.

::

  workon my_app
  pip install python-dev
  pip install python-setuptools
  pip install fabric

See also: http://www.fabfile.org/installing.html

**Install required Python packages**

::

  workon my_app
  cd ~/dev/my_app
  fab update_env

**Initialize the Database**

::

  workon my_app
  cd ~/dev/my_app
  fab reset_db         # Warning: This will delete all data in the database!

**Update configuration settings**

Before we can use this application, we will have to configure the database URL and SMTP account
that will be used to access the database and to send emails.

Instead of editing app/config/settings.py and checking in sensitive information into
the code repository, these settings can be set using OS environment variables
in your ``.bashrc`` or ``.bash_profile`` shell configuration file.

::

    export DATABASE_URL='sqlite:///app.sqlite'

    export MAIL_USERNAME='email@example.com'
    export MAIL_PASSWORD='password'
    export MAIL_DEFAULT_SENDER='MyApp" <noreply@example.com>'
    export MAIL_SERVER='smtp.gmail.com'
    export MAIL_PORT='465'
    export MAIL_USE_SSL='1'

    export ADMIN1='"Admin One" <admin1@example.com>'


Running the app
--------

**Start the development webserver**

Flask comes with a convenient WSGI web application server for development environments.

::

  workon my_app
  cd ~/dev/my_app
  fab runserver

Point your web browser to http://localhost:5000/

``fab reset_db`` will create one user with username 'admin' and password 'Password1'.


Automated tests and code coverage
--------
The tests are in the tests/ directory.

pytest is used to run the automated tests.

pytest is also used to run the code coverage assessment.

::

  workon my_app
  cd ~/dev/my_app
  fab test
  fab test_cov


Acknowledgements
--------
This project used `Flask-User-starter-app <https://github.com/lingthio/Flask-User-starter-app>`_ as a starting point.
