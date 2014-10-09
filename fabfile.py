# The 'fabfile.py' is used by Fabric and must reside in the application root directory.

from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from contextlib import contextmanager

@task
def runserver():
    """
    Start the web application using a development WSGI webserver provided by Flask
    """
    local('python runserver.py')


@task
def test_cov():
    """
    Run the automated test suite using py.test
    """
    local('py.test --tb=short -s  --cov app  --cov-config tests/.coveragerc  --cov-report term-missing  tests/')


@task
def test():
    """
    Run the automated test suite using py.test
    """
    local('py.test --tb=short -s tests/')


@task
def update_env():
    """
    Install required Python packages using pip and requirements.txt
    """
    local('if [ ! -f app/config/local_settings.py ]; then cp app/config/local_settings_example.py app/config/local_settings.py; fi')
    local('pip install -r requirements.txt')


@contextmanager
def virtualenv(venv_name):
    with prefix('source ~/.virtualenvs/'+venv_name+'/bin/activate'):
        yield
