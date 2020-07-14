import json
import os

from app import db
from app import current_project

from app.models.project_models import Project
from app.models.user_models import User
from app.models.data_pool_models import Image, ManualSegmentation, Message, Modality, ContrastType

"""
Return all project objects the current user is part of or all projects if the user is admin
"""
def get_all_projects():

    projects = db.session.query(Project).all()

    return projects

def get_projects_with_current_user():

    projects = current_user.admin_for_project.all() + \
        current_user.reviewer_for_project.all() + \
        current_user.user_for_project.all()

    return projects

def get_available_projects():

    projects = []

    # If the user is admin, return all projects
    if any(r.name == "admin" for r in current_user.roles):
        projects = get_all_projects()

    # Else only those he is part of
    else:
        projects = get_projects_with_current_user()

    return projects



