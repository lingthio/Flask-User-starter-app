# This directory contains Jinja2 template files

This Flask application uses the Jinja2 templating engine to render
data into HTML files.

The template files are organized into the following directories:

    common            # Common base templates and macros
    flask_user        # Flask-User template files (register, login, etc.)
    pages             # Templates for Page objects
    users             # Templates for User objects

Flask-User makes use of standard template files that reside in  
`PATH/TO/VIRTUALENV/lib/PYTHONVERSION/site-packages/flask_user/templates/flask_user/`.  
These standard templates can be overruled by placing a copy in the `app/templates/flask_user/` directory.
