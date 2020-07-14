# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import Blueprint, redirect, render_template, flash
from flask import request, url_for
from flask_user import current_user, login_required

from app import db, current_project
from app.models.project_models import Project
from app.models.user_models import User, UserProfileForm
from app.views.forms import ProjectForm

main_blueprint = Blueprint('view.main', __name__, template_folder='templates')


@main_blueprint.route('/')
@login_required
def default():
    """
    Return the project overview page that contains all projects the current user is part of
    """
    # Find the role of this user in the project
    return redirect("/project/overview")


@main_blueprint.route('/project/overview')
@login_required
def get_project_overview_page():
    """
    Return the project overview page that contains all projects the current user is part of
    """
    # Find the role of this user in the project
    return render_template("pages/project_overview.html")


@main_blueprint.route('/project/<int:project_id>')
@login_required
def project_redirect(project_id):
    """
    This function is used to redirect the user to the correct page, i.e. as admin, reviewer or user, depending
    on his role in the current project
    """

    if current_user in current_project.role_admins:
        return redirect(f'/project/{current_project.id}/admin/cases')
    elif current_user in current_project.role_reviewers:
        return redirect(f'/project/{current_project.id}/review/cases')
    elif current_user in current_project.role_users:
        return redirect(f'/project/{current_project.id}/segmentation/cases')
    else:
        flash('You are no member of this project.', category="error")
        return redirect(f'/project/overview')


@main_blueprint.route('/project/<int:project_id>/<string:role>/cases')
@login_required
def project_role_page(project_id, role):
    """
    A project can be accessed in three different roles: as admin, reviewer and user. This function
    checks that the user is authorised to access the chosen project in this role and returns the according
    page, if allowed.
    """

    # Data for various forms
    project_form = ProjectForm()

    # Build data object that contains all information for flask to use when building the page
    data = dict(current_project=current_project,
                role=role, project_form=project_form)
    
    if role == "admin":
        return render_template('pages/admin/cases.html', data=data)
    elif role == "review":
        return render_template('pages/review/cases.html', data=data)
    elif role == "segmentation":
        return render_template('pages/segmentation/cases.html', data=data)


@main_blueprint.route('/users')
@login_required
def users_page():
    return render_template('pages/users_page.html')

# The User page is accessible to authenticated users (users that have logged in)
@main_blueprint.route('/member')
@login_required  # Limits access to authenticated users
def member_page():
    return render_template('main/user_page.html')


@main_blueprint.route('/main/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    form = UserProfileForm(request.form, obj=current_user)

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('main.home_page'))

    # Process GET or invalid POST
    return render_template('main/user_profile_page.html',
                           form=form)
