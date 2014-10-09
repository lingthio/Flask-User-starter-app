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

**Install virtualenv and virtualenvwrapper**

virtualenv allows multiple Python applications to switch between multiple Python environments.

See http://virtualenvwrapper.readthedocs.org/en/latest/install.html

**Make a virtualenv**

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
  pip install fabric

**Install required Python packages**

::

  cd ~/dev/app
  workon app
  fab update_env


Automated tests and code coverage
------
The tests are in the tests/ directory.

pytest is used to run the automated tests. Use ``fab test`` to run them.

pytest is also used to run the code coverage assessment. Use ``fab test_cov`` to run them.


Running the app
~~~~~~~~

**Start the development webserver**

Flask comes with a convenient WSGI web application server for development environments.

::

  cd ~/dev/app
  workon app
  fab runserver

Point your web browser to http://localhost:5000/


Acknowledgements
~~~~~~~~
| This project used the Flask-User starter app as a starting point.
| See https://github.com/lingthio/Flask-User-starter-app