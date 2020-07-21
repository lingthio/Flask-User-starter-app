import json
import os

from flask import current_app as app

from flask_user import current_user

from app.models.data_pool_models import Modality, ContrastType
from app.models.project_models import Project
from app.models.user_models import User

from app import db

# PROJECTS

"""
Return all project objects the current user is part of or all projects if the user is admin
"""
def get_all_projects():

    projects = db.session.query(Project).all()

    return projects

"""
Tries to find a project by it's id

If no id is provided, logs error and returns None
"""
def find_project(id = None):

    if id:
        project = Project.query.get(id)
    else:
        app.logger.error("No parameters given for project search")
        
        return None

    return project

"""
Returns all projects in which the current user has a role in
"""
def get_projects_with_current_user():

    projects = current_user.admin_for_project.all() \
                + current_user.reviewer_for_project.all() \
                + current_user.user_for_project.all()

    return projects

"""
Returns all projects in which the current user has a role in or all existing projects if the current user is admin
"""
def get_available_projects():

    projects = []

    # If the user is admin, return all projects
    if any(r.name == "admin" for r in current_user.roles):
        projects = get_all_projects()

    # Else only those he is part of
    else:
        projects = get_projects_with_current_user()

    return projects

"""
Creates a new project with the given parameters
"""
def create_project(short_name = None, long_name = None, description = None, 
                    admins = None, reviewers = None, users = None):

    project = Project(short_name = short_name, long_name = long_name, description = description, admins = admins, reviewers = reviewers, users = users)

    db.session.add(project)
    db.session.commit()

    return project

"""
Updates a given project in the database
"""
def update_project(project):

    if project:
        db.session.add(project)
        db.session.commit()

    return project

"""
Deletes a given project in the database
"""
def delete_project(project):

    if project:
        db.session.delete(project)
        db.session.commit()

    return project

# END PROJECTS

