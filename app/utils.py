from functools import wraps
from flask_login import current_user
from flask import abort
from app import current_project


def project_admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_project or not current_user in current_project.role_admins:
            return abort(403)
        else:
            return func(*args, **kwargs)
    return decorated_view


def project_reviewer_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_project or not current_user in current_project.role_reviewers:
            return abort(403)
        else:
            return func(*args, **kwargs)
    return decorated_view


def project_user_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_project or not current_user in current_project.role_users:
            return abort(403)
        else:
            return func(*args, **kwargs)
    return decorated_view