# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import render_template
from flask_user import login_required, roles_accepted

from app import app


# The Home page is accessible to anyone
@app.route('/')
def home_page():
    return render_template('pages/home_page.html')

# The User page is accessible to authenticated users (users that have logged in)
@app.route('/user')
@login_required             # Limits access to authenticated users
def user_page():
    return render_template('pages/user_page.html')

# The Admin page is accessible to users with the 'admin' role
@app.route('/admin')
@roles_accepted('admin')    # Limits access to users with the 'admin' role
def admin_page():
    return render_template('pages/admin_page.html')
