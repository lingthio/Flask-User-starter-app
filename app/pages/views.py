# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import redirect, render_template, render_template_string
from flask import request, url_for
from flask_user import current_user

from app.app_and_db import app


#
# Home page
#
@app.route('/')
def home_page():
    return render_template('pages/home_page.html')

