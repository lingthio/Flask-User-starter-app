# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import redirect, render_template, render_template_string
from flask import request, url_for
from flask_user import current_user, login_required

from app.app_and_db import app, db
from app.users.forms import UserProfileForm

#
# User Profile form
#
@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    user_profile = current_user.user_profile
    form = UserProfileForm(request.form, user_profile)

    # Process valid POST
    if request.method=='POST' and form.validate():

        # Copy form fields to user_profile fields
        form.populate_obj(user_profile)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('home_page'))

    # Process GET or invalid POST
    return render_template('users/user_profile_page.html',
        form=form)

