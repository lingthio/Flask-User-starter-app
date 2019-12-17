import io
import json
import os
import zipfile
from datetime import datetime

import flask
import regex as re
from dateutil.parser import parse as parse_date_string
from flask import Blueprint, jsonify, request, redirect, flash
from flask_user import login_required, current_user
from sqlalchemy import DateTime, Date, or_
from werkzeug.utils import secure_filename

from app import db, local_settings
from app.models.data_pool_models import Image, ManualSegmentation
from app.models.project_models import Project
from app.models.user_models import User

data_blueprint = Blueprint('bp_data', __name__, template_folder='templates')


@data_blueprint.route("/project_data")
@login_required
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

    if role == "segmentation":
        # Find assigned and open cases
        filter_query = filter_query.join(ManualSegmentation, Image.id == ManualSegmentation.image_id).filter(
            Image.is_valid == True).filter(
            or_(ManualSegmentation.assignee_id == user_id,
                ManualSegmentation.status.in_(["na", "submitted", "remitted"])))
    if role == "validation":
        # Find submitted cases
        filter_query = filter_query.join(ManualSegmentation, Image.id == ManualSegmentation.image_id).filter(
            ManualSegmentation.status == "submitted")

    records = filter_query.slice(offset, offset + limit).all()
    records_total = query.count()
    records_filtered = filter_query.count()

    # Also attach the users of the project
    project_users = db.session.query(Project).filter(Project.id == project_id).first().users
    project_users = [user.as_dict() for user in project_users]

    data = {
        "draw": request.values["draw"],
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "project_users": project_users,
        "data": [entry.as_dict() for entry in records],
    }

    return jsonify(data)


@data_blueprint.route("/project_change_submission", methods=['POST'])
@login_required
def change_project():
    """
    View for the project settings dialog that handles form submissions
    """
    # Find the project ID via the referer header
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
        elif role == "validation":
            project.reviewers.append(user)
        elif role == "segmentation":
            project.users.append(user)
        else:
            return "Error: {} not a role".format(role)
    db.session.commit()
    return redirect(request.referrer)


@data_blueprint.route("/update_image_meta_data", methods=['POST'])
@login_required
def update_image_meta_data():
    """
    View for handling changes to datapool objects (assignments etc.)
    """
    image_object = request.json
    segmentation_object = image_object["manual_segmentation"]

    # Find the image and segmentation object
    image = db.session.query(Image).filter(Image.id == image_object["id"]).first()
    manual_segmentation = image.manual_segmentation

    # Update values for image
    for column in Image.__table__.columns:
        column_name = column.name
        value = image_object[column_name]
        if value is None:
            continue
        if value is not None and type(column.type) == DateTime or type(column.type) == Date:
            value = datetime.strptime(image_object[column_name], '%a, %d %b %Y %H:%M:%S %Z')
        setattr(image, column_name, value)

    # Update values for image
    for column in ManualSegmentation.__table__.columns:
        column_name = column.name
        value = segmentation_object[column_name]
        if value is not None and type(column.type) == DateTime or type(column.type) == Date:
            value = parse_date_string(value)

        setattr(manual_segmentation, column_name, value)

    db.session.commit()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@data_blueprint.route("/segmentation_data", methods=['POST', 'GET'])
@login_required
def segmentation_data():
    """
    Function to upload or download segmentations
    """
    r = request
    # Retrieve image data
    form = request.form
    if "segmentation-download-btn" in form:
        image_id = int(form["segmentation-download-btn"])
    else:
        image_id = int(form['segmentation-upload-btn'])
    image = db.session.query(Image).filter(Image.id == image_id).first()
    project = image.project

    # Upload new segmentation
    if "segmentation-upload-btn" in form:
        # Check that user actually appended file
        if 'file' not in request.files or request.files['file'].filename == '':
            flash('No file appended', category="error")
            return redirect(request.referrer)

        # Save mask
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(local_settings.DATA_DIRECTORY, project.short_name, "masks", image.name)
            file.save(file_path)

        # Depending on who uploaded the segmentation, change status
        if any(current_user.id == user.id for user in project.admins) or any(
                current_user.id == user.id for user in project.reviewers):
            image.manual_segmentation.status = "valid"
        else:
            image.manual_segmentation.status = "submitted"
        db.session.commit()
        return redirect(request.referrer)

    # Download image + segmentation
    elif "segmentation-download-btn" in form:
        # Find corresponding files
        image_path = os.path.join(local_settings.DATA_DIRECTORY, project.short_name, "images", image.name)
        segmentation_path = os.path.join(local_settings.DATA_DIRECTORY, project.short_name, "masks",
                                         image.manual_segmentation.name)

        # Check if the user marked the "work on segmentation" checkbox
        if "work_on_checkbox" in form:
            print("change")
            image.manual_segmentation.status = "assigned"
            image.manual_segmentation.assignee = current_user
            image.manual_segmentation.assigned_date = datetime.now()
            db.session.commit()

        # Create zip file
        data = io.BytesIO()
        with zipfile.ZipFile(data, mode='w') as z:
            z.write(image_path, image.name)
            z.write(segmentation_path, "mask.nii.gz")
        data.seek(0)

        # Download file
        return flask.send_file(
            data,
            mimetype='application/zip',
            as_attachment=True,
            attachment_filename='data.zip'
        )


@data_blueprint.route("/segmentation_review", methods=['POST'])
@login_required
def segmentation_review():
    """
    Function to handle the form data submitted by a reviewer
    """
    # Fetch form data
    form = request.form
    image_id = int(form["submit-btn"])
    image = db.session.query(Image).filter(Image.id == image_id).first()

    # Assign correct status
    if "radio_valid" in form:
        image.manual_segmentation.status = "valid"
    elif "radio_remitted" in form:
        image.manual_segmentation.status = "remitted"

    db.session.commit()
    return redirect(request.referrer)


@data_blueprint.route("/new_data", methods=['POST'])
@login_required
def new_data():
    """
    Function to handle upload of new data
    """
    # Fetch form data
    r = request
    project_id = int(r.form["upload-btn"])
    project = db.session.query(Project).filter(Project.id == project_id).first()

    # Check if image was actually uploaded
    if 'image' not in request.files or request.files['image'].filename == '':
        flash('No image appended', category="error")
        return redirect(request.referrer)

    # Save image to correct path
    image = r.files["image"]
    image_path = os.path.join(local_settings.DATA_DIRECTORY, project.short_name, "images", image.filename)
    image.save(image_path)

    # Add entry to db
    image = Image(project=project, name=image.filename)
    db.session.add(image)

    # If segmentation is also provided, add it
    if 'segmentation' in request.files and request.files["segmentation"].filename != "":
        segmentation = r.files["segmentation"]
        segmentation_path = os.path.join(local_settings.DATA_DIRECTORY, project.short_name, "masks",
                                         segmentation.filename)
        segmentation.save(segmentation_path)

        # Add entry to db
        segmentation = ManualSegmentation(project=project, image=image)
        db.session.add(segmentation)

    db.session.commit()
    return redirect(request.referrer)
