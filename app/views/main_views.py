# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import Blueprint, redirect, render_template, flash
from flask import request, url_for
from flask_user import current_user, login_required

from app import db
from app.models.project_models import Project
from app.models.user_models import User, UserProfileForm
from app.views.forms import ProjectForm

main_blueprint = Blueprint('main', __name__, template_folder='templates')


@main_blueprint.route('/')
@login_required
def default():
    """
    Return the projects overview page that contains all projects the current user is part of
    """
    # Find the role of this user in the project
    return redirect("/projects/overview")


@main_blueprint.route('/projects/overview')
@login_required
def get_projects_overview_page():
    """
    Return the projects overview page that contains all projects the current user is part of
    """
    # Find the role of this user in the project
    return render_template("pages/projects_overview.html")


@main_blueprint.route('/projects/<int:project_id>')
@login_required
def project_redirect(project_id):
    """
    This function is used to redirect the user to the correct page, i.e. as admin, reviewer or user, depending
    on his role in the current project
    """
    # Find the role of this user in the project
    project = db.session.query(Project).filter(Project.id == project_id).first()
    user = db.session.query(User).filter(User.id == current_user.id).first()
    if user in project.users:
        return redirect("/projects/{}/segmentation".format(project.id))
    if user in project.reviewers:
        return redirect("/projects/{}/review".format(project.id))
    if user in project.admins:
        return redirect("/projects/{}/admin".format(project.id))


@main_blueprint.route('/projects/<int:project_id>/<string:role>')
@login_required
def project_role_page(project_id, role):
    """
    A project can be accessed in three different roles: as admin, reviewer and user. This function
    checks that the user is authorised to access the chosen project in this role and returns the according
    page, if allowed.
    """
    # Find the current project
    current_project = db.session.query(Project).filter(Project.id == project_id).first()
    user = db.session.query(User).filter(User.id == current_user.id).first()

    # Data for various forms
    project_form = ProjectForm()

    # Add the permissions to the user object for the navbar
    if user in current_project.admins:
        setattr(user, "role", "admin")
    elif user in current_project.reviewers:
        setattr(user, "role", "reviewer")
    else:
        setattr(user, "role", "user")

    # Build data object that contains all information for flask to use when building the page
    data = dict(current_project=current_project, user=current_user,
                role=role, project_form=project_form)
    if role == "admin":
        if user not in current_project.admins:
            flash('No permission to access admin page', category="error")
            return redirect("/projects/" + str(project_id))

        return render_template('pages/admin_page.html', data=data)

    elif role == "review":
        if user not in current_project.admins and user not in current_project.reviewers:
            flash('No permission to access review page', category="error")
            return redirect("/projects/" + str(project_id))
        return render_template('pages/review_page.html', data=data)

    elif role == "segmentation":
        return render_template('pages/segmentation_page.html', data=data)


@main_blueprint.route('/users')
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
