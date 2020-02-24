import json
import json
import os

from flask import jsonify, request, redirect
from flask_user import login_required, current_user
from sqlalchemy import or_, asc, desc

from app import app
from app import db
from app import current_project
from app.models.data_pool_models import Image, ManualSegmentation, ContrastType, Modality
from app.models.project_models import Project
from app.models.user_models import User


@app.route('/data/project_overview')
@login_required
def project_overview():
    """
    Return all project objects the current user is part of or all projects if the user is admin
    """
    # If the user is admin, return all projects
    roles = current_user.roles
    if any(r.name == "admin" for r in roles):
        projects = db.session.query(Project).all()
        projects = [p.as_dict() for p in projects]

        # Also add all users of the system so that the admin may add them to a project
        users = db.session.query(User).all()
        users = [u.as_dict() for u in users]
        result = jsonify(dict(data=projects, users=users))

    # Else only those he is part of
    else:
        projects = current_user.admin_for_project.all() + current_user.reviewer_for_project.all() + \
                   current_user.user_for_project.all()
        projects = [p.as_dict() for p in projects]
        result = jsonify(dict(data=projects))

    return result


@app.route("/data/update_projects_metadata", methods=['POST'])
@login_required
def update_projects_metadata():
    """
    Update the projets meta data like names, description and users
    """
    # Find the project ID by looking at the submit button
    form = request.form
    r = request
    project_id = request.headers["project_id"]

    # Create new project if not available or update existing one otherwise
    if project_id == "":
        project = Project()
    else:
        project = db.session.query(Project).filter(Project.id == int(project_id)).first()

    # In case the delete button was pressed, just delete the project
    if "delete-btn" in form:
        db.session.delete(project)
        db.session.commit()
        return redirect("/")

    # Update project object
    project.short_name = form["short_name"]
    project.long_name = form["long_name"]
    project.description = form["description"]

    # Update users by first deleting all entries in corresponding tables and then adding those transmitted by form
    project.admins.clear()
    project.reviewers.clear()
    project.users.clear()
    user_emails = form.getlist("users[]")
    roles = form.getlist("roles[]")
    for email, role in zip(user_emails, roles):
        user = db.session.query(User).filter(User.email == email).first()
        if role == "admin":
            project.admins.append(user)
        elif role == "review":
            project.reviewers.append(user)
        elif role == "segmentation":
            project.users.append(user)
        else:
            return "Error: {} not a role".format(role)

    # Update modalities and contrast type
    [db.session.query(Modality).filter(Modality.id == m.id).delete() for m in project.modalities]
    [db.session.query(ContrastType).filter(ContrastType.id == c.id).delete() for c in project.contrast_types]
    project.modalities.clear()
    project.contrast_types.clear()

    modalities = form.getlist("modalities[]")
    contrast_types = form.getlist("contrast_types[]")
    for modality in modalities:
        modality = Modality(name=modality, project=project)
        db.session.add(modality)
    for contrast_type in contrast_types:
        contrast_type = ContrastType(name=contrast_type, project=project)
        db.session.add(contrast_type)

    db.session.commit()

    # Create directory if not exist
    image_directory = os.path.join(app.config['DATA_PATH'], project.short_name, "images")
    mask_directory = os.path.join(app.config['DATA_PATH'], project.short_name, "masks")
    os.makedirs(image_directory, exist_ok=True)
    os.makedirs(mask_directory, exist_ok=True)

    return redirect(request.referrer)
