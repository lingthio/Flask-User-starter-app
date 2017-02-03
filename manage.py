# This file starts the WSGI web application.
# - Heroku starts gunicorn, which loads Procfile, which starts manage.py
# - Developers can run it from the command line: python runserver.py

from app.init_app import app, init_app, manager

# Start a development web server, processing extra command line parameters. E.g.:
# - python manage.py init_db
# - python manage.py runserver
if __name__ == "__main__":
    init_app(app)
    manager.run()
