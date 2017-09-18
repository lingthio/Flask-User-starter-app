# This file uses the Flask-Script 'manager'
# to start a Flask development application server.

from app.application import app as the_app, init_app

# Start a development web server if executed from the command line
if __name__ == "__main__":
    # Manage the command line parameters such as:
    # - python manage.py runserver
    # - python manage.py db
    init_app(the_app)
    from app.application import manager
    manager.run()
