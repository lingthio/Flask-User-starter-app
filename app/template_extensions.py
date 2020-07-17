
from app import app, user_manager
import app.utils as utils 
from app.controllers import project_controller

from flask_user import current_user

@app.context_processor
def user_manager():
    return dict(user_manager=user_manager)

@app.context_processor
def is_logged_in():
    return dict(is_logged_in=utils.is_logged_in())

# add current_project to template engine
@app.context_processor
def current_project():
    # app.logger.debug(f"context_processor - current_project {utils.get_current_project()}")
    return dict(current_project=utils.get_current_project())

# add all_projects to template engine
@app.context_processor
def all_projects():
    app.logger.debug(f"context_processor - all_projects {project_controller.get_all_projects()}")
    return dict(all_projects=project_controller.get_all_projects())

@app.context_processor
def is_technical_admin():
    # app.logger.debug(f"context_processor - is_technical_admin {utils.is_technical_admin()}")
    return dict(is_technical_admin=utils.is_technical_admin())

@app.context_processor
def is_project_admin():
    current_project = utils.get_current_project()
    # app.logger.debug(f"context_processor - is_project_admin {utils.is_project_admin(current_project)}")
    return dict(is_project_admin=utils.is_project_admin(current_project))

@app.context_processor
def is_project_reviewer():
    current_project = utils.get_current_project()
    # app.logger.debug(f"context_processor - is_project_reviewer {utils.is_project_reviewer(current_project)}")
    return dict(is_project_reviewer=utils.is_project_reviewer(current_project))

@app.context_processor
def is_project_user():
    current_project = utils.get_current_project()
    # app.logger.debug(f"context_processor - is_project_user {utils.is_project_user(current_project)}")
    return dict(is_project_user=utils.is_project_user(current_project))
