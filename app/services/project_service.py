import json
import os
import logging

from flask import Blueprint, jsonify, request, redirect, abort
from flask_user import login_required, current_user
from sqlalchemy import or_, asc, desc

from app import app, db
from app import current_project
from app.models.data_pool_models import Image, ManualSegmentation, ContrastType, Modality
from app.models.project_models import Project
from app.models.user_models import User

from app.controllers import project_controller, user_controller

from app.utils import technical_admin_required, project_admin_required, project_reviewer_required, project_user_required

# Define the blueprint: 'project_service', set its url prefix: app.url/project
project_service = Blueprint('project_service', __name__, url_prefix='/project')

"""
Return all project objects the current user is part of or all projects if the user is admin
"""
@project_service.route('/all', methods=['GET'])
@login_required
def all_projects():

    projects = project_controller.get_available_projects()

    projects = [p.as_dict() for p in projects]

    data = {
        "projects": projects
    }

    return jsonify(data)


"""
Update the project: names, description and users
"""
@project_service.route("", methods=['POST'])
@login_required
@technical_admin_required
def create_project():

    # check, if the request is fired by a form or by ajax call
    is_form_request = hasattr(request, 'form')

    app.logger.info(f"create_project: is form request {is_form_request}")

    project_data = None
    if is_form_request:
        project_data = request.form
    else:
        project_data = json.loads(request.data)

    app.logger.info(project_data)

    return redirect(request.referrer)


"""
Update the project: names, description and users
"""
@project_service.route("", methods=['PUT', 'POST'])
@login_required
@project_admin_required
def create_or_update_project():

    # project ID needs to be in the url like /project?id=1
    project_id = request.args.get('id')

    creating_new_project = False

    if not project_id:
        creating_new_project = True
        #return abort(401, "Error: No project id provided. ( like /project?id=1 )")

    app.logger.info(project_id)

    # check, if the request is fired by a form or by ajax call
    is_form_request = hasattr(request, 'form')

    app.logger.info(f"update_project: is form request {is_form_request}")

    # these are filled different regarding whether data comes from form or from json
    users = None
    modalities = None
    contrast_types = None

    project_data = None

    # either get the data from a FormData object or from a JSON Object
    # it only differs for users, modalities and contrast_types
    if is_form_request:
        project_data = request.form

        user_emails = request.form.getlist("users[]")
        user_roles = request.form.getlist("roles[]")

        users = [user for user in zip(user_emails, user_roles)]

        modalities = request.form.getlist("modalities[]")
        contrast_types = request.form.getlist("contrast_types[]")
    else:
        project_data = json.loads(request.data)

        users = project_data["users"]
        modalities = project_data["modalities"]
        contrast_types = project_data["contrast_types"]

    app.logger.info(project_data)

    # TODO Abfangen, dass short_name nicht so gesetzt wird, dass der String nicht in einem Datei-Pfad verwendet werden kann (siehe unten: os.makedirs(...))

    short_name = project_data["short_name"]
    long_name = project_data["long_name"]
    description = project_data["description"]

    app.logger.info(short_name)
    app.logger.info(long_name)
    app.logger.info(description)
    app.logger.info(users)
    app.logger.info(modalities)
    app.logger.info(contrast_types)

    project_admins = []
    project_reviewers = []
    project_users = []

    for email, role in users:
        user = user_controller.find_user(email = email)

        if not user:
            return abort(401, f"Error: User with email address {email} does not exist.")

        if role == "admin":
            project_admins.append(user)
        elif role == "review":
            project_reviewers.append(user)
        elif role == "segmentation":
            project_users.append(user)
        else:
            return abort(401, f"Error: {role} is not a role.")
            
    # Create new project if not available or update existing one otherwise
    if creating_new_project:
        project = project_controller.create_project(short_name = short_name, long_name = long_name, description = description, 
                                                    admins = project_admins, reviewers = project_reviewers, users = project_users)

        # Create directories for data
        image_directory = os.path.join(app.config['DATA_PATH'], project.short_name, "images")
        mask_directory = os.path.join(app.config['DATA_PATH'], project.short_name, "masks")

        os.makedirs(image_directory, exist_ok=False)
        os.makedirs(mask_directory, exist_ok=False)
    else:
        project = project_controller.find_project(id=project_id)

        if not project:
            return abort(401, f"Error: Project with id {project_id} does not exist.")

        # rename the project directory if the short name is changed
        if project.short_name != short_name:
            old_project_directory = os.path.join(app.config['DATA_PATH'], project.short_name)
            new_project_directory = os.path.join(app.config['DATA_PATH'], short_name)

            os.rename(old_project_directory, new_project_directory)

        project.short_name = short_name
        project.long_name = long_name
        project.description = description

        # Update members of project
        project.admins = project_admins
        project.reviewers = project_reviewers
        project.users = project_users

        # Delete old modalities
        for modality in project.modalities:
            modality = project_controller.find_modality(id = modality.id)

            if modality:
                project_controller.delete_modality(modality)

        project.modalities.clear()

        # Delete old contrast types
        for contrast_type in project.contrast_types:
            contrast_type = project_controller.find_contrast_type(id = contrast_type.id)

            if contrast_type:
                project_controller.delete_contrast_type(contrast_type)
        
        project.contrast_types.clear()

        project_controller.update_project(project)

    # Update modalities (after project update / creation, because we need the project object)

    # Create new modalities
    for modality in modalities:
        modality = project_controller.create_modality(name = modality, project_id = project.id)

    # Create new contrast types
    for contrast_type in contrast_types:
        contrast_type = project_controller.create_contrast_type(name = contrast_type, project_id = project.id)

    data = {
        "project": project.as_dict()
    }

    return jsonify(data)


"""
Deletes the project
"""
@project_service.route("", methods=['DELETE'])
@login_required
@project_admin_required
def delete_project():
    # project ID needs to be in the url like /project?id=1
    project_id = request.args.get('id')

    if not project_id:
        return abort(401, "Error: No project id provided. ( like /project?id=1 )")

    project = project_controller.find_project(id = project_id)

    if project:
        is_project_deleted = project_controller.delete_project(project)
    else:
        is_project_deleted = False

    app.logger.info(f"project deleted {is_project_deleted}")

    data = {
        "success": is_project_deleted
    }

    return jsonify(data)
    