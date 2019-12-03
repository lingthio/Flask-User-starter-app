from flask import Blueprint, render_template, jsonify, request, redirect
from app import db
from app.models.data_pool_models import Image, DataPool
from app.models.project_models import Project, ProjectsAdmins, ProjectsReviewers, ProjectsUsers
from app.models.user_models import User
from app.views.forms import ProjectForm
import regex as re

data_blueprint = Blueprint('bp_data', __name__, template_folder='templates')


@data_blueprint.route("/project_data")
def get_data():
    """
    Get all entries of the data tables according to the project, role and user id specified in request headers
    """
    # Extract meta info from request headers
    project_id = int(request.headers.get("project_id"))
    user_id = int(request.headers.get("user_id"))
    role = request.headers.get("role")
    offset = int(request.values["start"])
    limit = int(request.values["length"])

    # Build query and fetch results
    query = db.session.query(Image)
    filter_query = query.filter(Image.project_id == project_id)
    records = filter_query.slice(offset, offset + limit).all()

    records_total = query.count()
    records_filtered = filter_query.count()

    data = {
        "draw": request.values["draw"],
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "data": [entry.as_dict() for entry in records],
    }

    return jsonify(data)


@data_blueprint.route("/project_change_submission", methods=['POST'])
def change_project():
    """
    View for the project settings dialog that handles form submissions
    """
    # Find the project ID via the referer header
    r = request
    form = request.form
    project_id = int(re.match(r'.*projects/(\d+)/.*', str(request.referrer))[1])
    project = db.session.query(Project).filter(Project.id == project_id).first()

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
    user_ids = form.getlist("users[]")
    roles = form.getlist("roles[]")
    for user_id, role in zip(user_ids, roles):
        user = db.session.query(User).filter(User.id == int(user_id)).first()
        if role == "admin":
            project.admins.append(user)
        elif role == "reviewer":
            project.reviewers.append(user)
        elif role == "user":
            project.users.append(user)
        else:
            return "Error: {} not a role".format(role)
    db.session.commit()
    return redirect(request.referrer)
