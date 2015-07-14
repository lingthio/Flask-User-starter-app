# This file starts the WSGI web application.
# - Heroku starts gunicorn, which loads Procfile, which starts runserver.py
# - Developers can run it from the command line: python runserver.py

from app import create_app

app = create_app()

# Start a development web server if executed from the command line
if __name__ == "__main__":
    app.run(port=5000, debug=True)
