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
* Flask-User


Installation
~~~~~~~~

**Install git**

See http://git-scm.com/book/en/Getting-Started-Installing-Git

**Clone this github repository**

Open a command line shell and type:

::

  mkdir -p ~/dev
  cd ~/dev
  git clone https://github.com/lingthio/Flask-User-starter-app.git app
  cd ~/dev/app

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

  mkvirtualenv -p /full/path/to/python2.7 app
  workon app

where the result of ``which python`` can be used instead of ``/full/path/to/python2.7``,
and where ``app`` is the name of the new virtualenv.

**Install Fabric**

Fabric is a build and deployment tool that uses the Python language for its scripts.
Though the product name is 'Fabric', the command line tool is 'fab'.

::

  workon app
  pip install python-dev
  pip install python-setuptools
  pip install fabric

See also: http://www.fabfile.org/installing.html

**Install required Python packages**

::

  workon app
  cd ~/dev/app
  fab update_env

**Update configuration settings**

Before we can use this application, we will have to configure the SMTP account that it will be using to send emails.

Make sure that app/config/local_settings.py exists, or create it from a copy of local_settings_example.py file

Edit app/config/local_settings.py and configure the following settings:

* MAIL_USERNAME
* MAIL_PASSWORD
* MAIL_DEFAULT_SENDER
* ADMINS


Automated tests and code coverage
------
The tests are in the tests/ directory.

pytest is used to run the automated tests.

pytest is also used to run the code coverage assessment.

::

  workon app
  cd ~/dev/app
  fab test
  fab test_cov


Running the app
~~~~~~~~

**Start the development webserver**

Flask comes with a convenient WSGI web application server for development environments.

::

  workon app
  cd ~/dev/app
  fab runserver

Point your web browser to http://localhost:5000/


Creating a user account
~~~~~~~
* Make sure that app/config/local_settings.py has the appropriate ``MAIL_*`` settings.
* Point your web browser to http://localhost:5000/
* Click on 'Sign in' and then 'Register' and register a new user account.
* Confirm your email address


Acknowledgements
~~~~~~~~
This project used `Flask-User-starter-app <https://github.com/lingthio/Flask-User-starter-app>`_ as a starting point.
