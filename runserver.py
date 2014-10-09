#!/Users/lingthio/envs/glamdring/bin/python

# The 'runserver.py' file is used to run a Flask application
# using the development WSGI web server provided by Flask.
# Run 'python runserver.py' and point your web browser to http://localhost:5000/


from app.app_and_db import app, db
from app.startup.init_app import init_app

init_app(app, db)
app.run(port=5000, debug=True)
