# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import Blueprint, redirect, render_template
from flask import request, url_for
from flask_user import current_user, login_required

from app import db
from app.models.project_models import Project
from app.models.user_models import User, UserProfileForm
from app.views.forms import ProjectForm

main_blueprint = Blueprint('main', __name__, template_folder='templates')


@main_blueprint.route('/')
@login_required
def default_path():
    """
    In case a user acceses the root page, he is redirected to the page of the first
    project in the database he is a part of with the tab chosen according to his
    role.
    """
    # Try to find a project and the role of the user in this project
    project = current_user.admin_for_project.first()
    if project is not None:
        return redirect("projects/{}/admin".format(project.id))
    project = current_user.reviewer_for_project.first()
    if project is not None:
        return redirect("projects/{}/validation".format(project.id))
    project = current_user.user_for_project.first()
    if project is not None:
        return redirect("projects/{}/segmentation".format(project.id))
    else:
        return "You are not part of a project yet"  # ToDo


@main_blueprint.route('/projects/<int:project_id>/')
@login_required
def project_page(project_id):
    """
    In case a user acceses a project page without specifying the role, he is redirected
    to the corresponding page according to his role in this project
    """
    # Find the role of this user in the project
    project = db.session.query(Project).filter(Project.id == project_id).first()
    user = db.session.query(User).filter(User.id == current_user.id).first()
    if user in project.users:
        return redirect("/projects/{}/segmentation".format(project.id))
    if user in project.reviewers:
        return redirect("/projects/{}/validation".format(project.id))
    if user in project.admins:
        return redirect("/projects/{}/admin".format(project.id))
    print("")


@main_blueprint.route('/projects/<int:project_id>/<string:role>')
@login_required
def project_role_page(project_id, role):
    """
    A project can be accessed in three different roles: as admin, reviewer and user. This function
    checks that the user is authorised to access the chosen project in this role and returns the according
    page, if allowed.
    """
    # Find all Projects the current user is a part of
    u = current_user
    projects = list(set(u.admin_for_project.all() + u.reviewer_for_project.all() + u.user_for_project.all()))
    active_project = db.session.query(Project).filter(Project.id == project_id).first()

    # Find all users that are part of this project and add their role in the current project to the object
    for user in active_project.users:
        user.role = "segmentation"
    for user in active_project.reviewers:
        user.role = "validation"
    for user in active_project.admins:
        user.role = "admin"
    project_users = active_project.users + active_project.reviewers + active_project.admins

    # Find all users that are not part of this project
    all_users = db.session.query(User).all()

    # Data for various forms
    project_form = ProjectForm()

    # Build data object that contains all information for flask to use when building the page
    data = dict(projects=projects, project_users=project_users, active_project=active_project, user=current_user,
                role=role, project_form=project_form, all_users=all_users)
    if role == "admin":
        return render_template('main/admin_page.html', data=data)
    elif role == "segmentation":
        return render_template('main/segmentation_page.html', data=data)
    elif role == "validation":
        return render_template('main/validation_page.html', data=data)


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
