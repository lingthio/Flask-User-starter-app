# This directory contains all the unit tests for this Flask application.
# pytest is used to run these tests (pytest is more 'pythonic' than unittest).

File             Description
-------------    -----------
.coverage      # Configuration file for the test coverage tool (fab test_cov)
conftest.py    # Contains module level test fixtures for pytest
               # pytest requires this file to be 'conftest.py'
test_*.py      # Unit test files
               # pytest requires these files to start with the name 'test'


Install
-------

pytest is installed using
   pip install pytest
The command line tool is named 'py.test' (with a dot)


Usage
-----

Tests are run from the root directory:
   py.test -s tests/

Code coverage is performed from the root directory:
   py.test -s  --cov app  --cov-config tests/.coveragerc  --cov-report term-missing  tests/')